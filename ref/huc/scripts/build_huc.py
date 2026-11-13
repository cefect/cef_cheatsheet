"""Fetch bounded basemap inputs and render the nested Upper Colorado collection."""

import argparse, csv, datetime, hashlib, json, logging, pathlib, time, urllib.parse, urllib.request
import numpy as np
import yaml
from osgeo import gdal, ogr, osr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as effects
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.collections import LineCollection
from pyproj import Transformer


def main_build_huc(config_path, logger=None):
    """Cache sources, report topology tolerances, and create printable PDFs."""
    start = time.monotonic()
    log = logger or logging.getLogger(__name__)
    config = yaml.safe_load(pathlib.Path(config_path).read_text())
    paths = {key: pathlib.Path(config["paths"][key]) for key in ["build", "downloads", "prepared", "maps", "site"]}
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    log.info(f"Building HUC collection\n    {paths['build']}")
    log.debug(f"Configuration: {config}")
    ogr.UseExceptions()
    gdal.UseExceptions()
    target = osr.SpatialReference()
    target.ImportFromEPSG(5070)
    target.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    units, lookup = {}, []
    archive = paths["downloads"] / "WBD_14_HU2_Shape.zip"
    # Read the single WBD release into a common projected coordinate system.
    for level in config["levels"]:
        log.debug(f"Reading HUC{level}")
        source = ogr.Open(f"/vsizip/{archive.resolve()}/Shape/WBDHU{level}.shp")
        layer = source.GetLayer(0)
        crs = layer.GetSpatialRef()
        crs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        transform = osr.CoordinateTransformation(crs, target)
        units[level] = {}
        for feature in layer:
            code = feature.GetField(f"huc{level}")
            assert len(code) == level and code.startswith(config["region"]["code"])
            assert code not in units[level]
            geometry = feature.GetGeometryRef().Clone()
            assert geometry.IsValid() and not geometry.IsEmpty()
            geometry.Transform(transform)
            units[level][code] = geometry
            lookup.append([level, code, feature.GetField("name"), code[:-2] if level > 2 else ""])
    region = units[2][config["region"]["code"]]
    x0, x1, y0, y1 = region.GetEnvelope()
    width, height = (x1-x0)*1.1, (y1-y0)*1.1
    ratio = config["page"]["frame_width_in"] / config["page"]["slots_height_in"]["map"]
    width, height = max(width, height*ratio), max(height, width/ratio)
    bounds = [(x0+x1-width)/2, (y0+y1-height)/2, (x0+x1+width)/2, (y0+y1+height)/2]
    frame = {"bounds": bounds, "crs": "EPSG:5070", "width_px": 2400, "height_px": 2625}
    (paths["prepared"] / "frame.json").write_text(json.dumps(frame, indent=2))
    # Check spatial coverage for each parent; preserve all original boundaries.
    if not (paths["build"] / "topology.json").exists():
        topology = []
        for level in config["levels"][1:]:
            for parent, geometry in units[level-2].items():
                children = [g for code, g in units[level].items() if code[:-2] == parent]
                assert children, parent
                multi = ogr.Geometry(ogr.wkbMultiPolygon)
                for child in children:
                    if ogr.GT_Flatten(child.GetGeometryType()) == ogr.wkbPolygon:
                        multi.AddGeometry(child)
                    else:
                        for polygon in child:
                            multi.AddGeometry(polygon)
                union = multi.UnionCascaded()
                topology.append({"parent": parent, "children": len(children), "gap_m2": geometry.Difference(union).GetArea(), "outside_m2": union.Difference(geometry).GetArea(), "overlap_m2": max(0, sum(g.GetArea() for g in children)-union.GetArea())})
        (paths["build"] / "topology.json").write_text(json.dumps({"reporting_tolerance_m2": 100, "parents": topology}, indent=2))
        log.info(f"Validated {len(lookup):,} units and {len(topology):,} parent groups")
    # Request a bounded elevation raster from the USGS 3DEP source service.
    parameters = {"f": "image", "bbox": ",".join(map(str, bounds)), "bboxSR": 5070, "imageSR": 5070, "size": "2400,2625", "format": "tiff", "pixelType": "F32", "interpolation": "RSP_BilinearInterpolation"}
    dem_url = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?" + urllib.parse.urlencode(parameters)
    dem = paths["downloads"] / "terrain.tif"
    fetch(dem_url, dem)
    dataset = gdal.Open(str(dem))
    assert dataset.RasterXSize == 2400 and dataset.RasterYSize == 2625
    raster = dataset.ReadAsArray()
    assert np.isfinite(raster).all() and np.std(raster) > 1
    shade_path = paths["prepared"] / "basemap.tif"
    gdal.DEMProcessing(str(shade_path), dataset, "hillshade", computeEdges=True)
    shade = gdal.Open(str(shade_path)).ReadAsArray()
    # OSM context is a bounded Overpass extract; no public raster tile scraping.
    transformer = Transformer.from_crs(5070, 4326, always_xy=True)
    lon0, lat0, lon1, lat1 = transformer.transform_bounds(*bounds, densify_pts=41)
    bbox = f"{lat0},{lon0},{lat1},{lon1}"
    query = f'[out:json][timeout:180];(way[waterway=river]({bbox});way[highway=motorway]({bbox});node[place~"^(city|town)$"]({bbox}););out geom;'
    osm_url = "https://overpass-api.de/api/interpreter?" + urllib.parse.urlencode({"data": query})
    osm_path = paths["downloads"] / "osm-context.json"
    fetch(osm_url, osm_path)
    osm = json.loads(osm_path.read_text())
    assert osm.get("elements") and "remark" not in osm, osm.get("remark")
    to_map = Transformer.from_crs(4326, 5070, always_xy=True)
    context = []
    for element in osm["elements"]:
        if "geometry" in element:
            context.append(np.array([to_map.transform(p["lon"], p["lat"]) for p in element["geometry"]]))
    # HUC-001: dashed Census state borders provide geographic context on every sheet.
    states_url = "https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_500k.zip"
    states_path = paths["downloads"] / "cb_2024_us_state_500k.zip"
    fetch(states_url, states_path)
    source = ogr.Open(f"/vsizip/{states_path.resolve()}/cb_2024_us_state_500k.shp")
    layer = source.GetLayer(0)
    crs = layer.GetSpatialRef()
    crs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    transform = osr.CoordinateTransformation(crs, target)
    state_lines = []
    for feature in layer:
        geometry = feature.GetGeometryRef().Clone()
        geometry.Transform(transform)
        envelope = geometry.GetEnvelope()
        if envelope[1] >= bounds[0] and envelope[0] <= bounds[2] and envelope[3] >= bounds[1] and envelope[2] <= bounds[3]:
            state_lines.extend(rings(geometry))
    outlet_points = locate_outlets({"archive": archive, "units": {level: group for level, group in units.items() if level <= 8}, "osm": osm, "to_map": to_map, "target": target})
    (paths["build"] / "outlets.json").write_text(json.dumps(outlet_points, indent=2))
    # Render all pages with an identical physical frame and exact shared basemap.
    omitted = {}
    with (paths["site"] / config["paths"]["lookup_filename"]).open("w") as stream:
        writer = csv.writer(stream)
        writer.writerow(["level", "code", "name", "parent"])
        writer.writerows(lookup)
    with PdfPages(paths["site"] / config["paths"]["collection_filename"]) as collection:
        for level in config["levels"]:
            fig = plt.figure(figsize=(8.5, 11))
            ax = fig.add_axes([0.25/8.5, 1.5/11, 8/8.5, 8.75/11])
            ax.imshow(shade, extent=[bounds[0], bounds[2], bounds[1], bounds[3]], cmap="gray", vmin=-300, vmax=255, interpolation="bilinear")
            ax.add_collection(LineCollection(context, colors="0.65", linewidths=0.25))
            for draw_level in sorted(set([2, max(2, level-2), level]), reverse=True):
                lines = []
                for geometry in units[draw_level].values():
                    lines.extend(rings(geometry.SimplifyPreserveTopology(100)))
                ax.add_collection(LineCollection(lines, colors="0.15" if draw_level == 2 else "0.3", linewidths=1.4 if draw_level == 2 else 0.4))
            ax.add_collection(LineCollection(state_lines, colors="0.25", linewidths=0.9, linestyles=(0, (10, 8))))
            ax.set(xlim=(bounds[0], bounds[2]), ylim=(bounds[1], bounds[3]))
            ax.set_aspect("equal")
            ax.set_xticks([])
            ax.set_yticks([])
            # HUC-001: nested open circles retain the coarser outlet hierarchy.
            for outlet_level in config["levels"]:
                if level > 8 or outlet_level > level:
                    break
                for record in outlet_points[str(outlet_level)].values():
                    if record["point"] is not None:
                        ax.plot(*record["point"], marker="o", markersize=config["outlets"]["marker_diameter_pt"][outlet_level], markerfacecolor="none", markeredgecolor="black", markeredgewidth=1.2, zorder=10)
            fig.canvas.draw()
            occupied, placed = [], 0
            for code, geometry in (sorted(units[level].items(), key=lambda item: -item[1].GetArea()) if level in config["style"]["labels"]["enabled_levels"] else []):
                point = geometry.PointOnSurface()
                title = code if level > 2 else "14\nUpper Colorado"
                text = ax.text(point.GetX(), point.GetY(), title, fontsize=12, ha="center", va="center", path_effects=[effects.withStroke(linewidth=2, foreground="white")])
                box = text.get_window_extent(fig.canvas.get_renderer()).expanded(1.15, 1.2)
                if any(box.overlaps(previous) for previous in occupied):
                    text.remove()
                else:
                    occupied.append(box)
                    placed += 1
            omitted[level] = len(units[level])-placed
            # HUC-001: identify each map and its complete unit count at lower left.
            fig.text(1-0.25/8.5, 10.5/11, f"HUC {level:02d}", fontsize=16.8, weight="bold", ha="right")
            fig.text(0.25/8.5, 1.2/11, f"{len(units[level]):,} total units", fontsize=12)
            # HUC-001: match legend circles to the outlet hierarchy on this page.
            legend_handles = [plt.Line2D([], [], linestyle="none", marker="o", markersize=config["outlets"]["marker_diameter_pt"][outlet_level], markerfacecolor="none", markeredgecolor="black", markeredgewidth=1.2, label=f"HU{outlet_level} outlet") for outlet_level in config["levels"] if outlet_level <= level and level <= 8]
            if legend_handles:
                fig.legend(handles=legend_handles, loc="lower left", bbox_to_anchor=(0.25/8.5, 0.3/11), bbox_transform=fig.transFigure, ncol=2, fontsize=12, frameon=False, borderaxespad=0, handletextpad=0.7, columnspacing=1.6, labelspacing=0.8)
            sx, sy = bounds[0]+width*.05, bounds[1]+height*.05
            ax.plot([sx, sx+100000], [sy, sy], color="black", lw=2)
            ax.text(sx+50000, sy+height*.015, "100 km", fontsize=12, ha="center")
            # Keep mandatory map-data attribution unobtrusive along the map edge.
            fig.text(0.985, 0.5, "© OpenStreetMap contributors · openstreetmap.org/copyright | USGS | US Census Bureau", fontsize=6, rotation=90, ha="center", va="center")
            fig.savefig(paths["site"] / f"huc{level:02d}.pdf")
            if level in [2, 4, 6, 8, 10, 12]:
                fig.savefig(paths["maps"] / f"huc{level:02d}-preview.png", dpi=100)
            collection.savefig(fig)
            plt.close(fig)
    # Pin source bytes, source timestamps, coverage, and labeling limits.
    manifest = {"built_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "frame": frame, "label_omissions": omitted, "osm_timestamp": osm.get("osm3s"), "sources": []}
    for path, url, license_name in [(archive, "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_14_HU2_Shape.zip", "USGS public domain"), (dem, dem_url, "USGS public domain"), (osm_path, osm_url, "ODbL"), (states_path, states_url, "US Census Bureau public domain")]:
        manifest["sources"].append({"path": str(path), "url": url, "license": license_name, "bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    pathlib.Path(config["paths"]["manifest"]).write_text(json.dumps(manifest, indent=2))
    for path in paths.values():
        (path / "README.md").write_text("# HUC generated products\n\n- Producer: `ref/huc/scripts/build_huc.py`.\n" + "".join(f"- `{child.name}`\n" for child in sorted(path.iterdir()) if child.name != "README.md"))
    log.info(f"Rendered configured sheets and collection in {time.monotonic()-start:.1f} s\n    {paths['site']}")


def locate_outlets(inputs):
    """Infer primary outlets from WBD HU12 routing and OSM river crossings.

    Closed units have no marker; missing river coverage is reported explicitly.
    Markers sharing a terminal HU12 reuse a single coordinate across levels.
    """
    source = ogr.Open(f"/vsizip/{inputs['archive'].resolve()}/Shape/WBDHU12.shp")
    layer = source.GetLayer(0)
    crs = layer.GetSpatialRef()
    crs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    transform = osr.CoordinateTransformation(crs, inputs["target"])
    routing, polygons, area = {}, {}, {}
    for feature in layer:
        code = feature["huc12"]
        routing[code] = feature["tohuc"]
        polygons[code] = feature.GetGeometryRef().Clone()
        polygons[code].Transform(transform)
        area[code] = polygons[code].GetArea()
    # Accumulate upstream area to select the main routed exit of each unit.
    remaining = {code: 0 for code in routing}
    for downstream in routing.values():
        if downstream in remaining:
            remaining[downstream] += 1
    queue = [code for code in remaining if remaining[code] == 0]
    for code in queue:
        downstream = routing[code]
        if downstream in remaining:
            area[downstream] += area[code]
            remaining[downstream] -= 1
            if remaining[downstream] == 0:
                queue.append(downstream)
    if len(queue) != len(routing):
        raise ValueError("Cycle in WBD HU12 routing")
    rivers = []
    for element in inputs["osm"]["elements"]:
        if element.get("tags", {}).get("waterway") == "river" and "geometry" in element:
            line = ogr.Geometry(ogr.wkbLineString)
            for point in element["geometry"]:
                line.AddPoint_2D(*inputs["to_map"].transform(point["lon"], point["lat"]))
            rivers.append(line)
    results, shared = {}, {}
    for level, units in inputs["units"].items():
        results[str(level)] = {}
        for code, polygon in units.items():
            exits = [child for child, downstream in routing.items() if child.startswith(code) and downstream.isdigit() and not downstream.startswith(code)]
            if not exits:
                results[str(level)][code] = {"point": None, "status": "closed; no routed external exit"}
                continue
            terminal = max(exits, key=lambda child: area[child])
            if terminal not in shared:
                boundary = polygon.Boundary().Intersection(polygons[terminal].Buffer(100))
                downstream = routing[terminal]
                # Parent boundary avoids tiny mismatches between adjacent HU12 edges.
                candidates = []
                envelope = boundary.GetEnvelope()
                for river in rivers:
                    other = river.GetEnvelope()
                    if other[1] < envelope[0] or other[0] > envelope[1] or other[3] < envelope[2] or other[2] > envelope[3]:
                        continue
                    crossing = boundary.Intersection(river)
                    if not crossing.IsEmpty():
                        # Most source crossings are single points; retain multipart points.
                        parts = [crossing] if crossing.GetGeometryName() == "POINT" else list(crossing)
                        for point in parts:
                            if point.GetGeometryName() == "POINT":
                                candidates.append((river.Length(), [point.GetX(), point.GetY()]))
                shared[terminal] = max(candidates, key=lambda item: item[0])[1] if candidates else None
            results[str(level)][code] = {"point": shared[terminal], "terminal_huc12": terminal, "status": "WBD routing / OSM crossing inferred" if shared[terminal] else "unresolved river crossing"}
    results["2"]["14"]["point"] = list(inputs["to_map"].transform(-111.588412863279, 36.86458961678))
    terminal = results["2"]["14"]["terminal_huc12"]
    for units in results.values():
        for record in units.values():
            if record.get("terminal_huc12") == terminal:
                record["point"] = results["2"]["14"]["point"]
    return results


def fetch(url, path):
    """Cache complete downloads and retain response metadata alongside them."""
    if path.exists():
        return
    request = urllib.request.Request(url, headers={"User-Agent": "cef-cheatsheet-huc/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=240) as response:
                data = response.read()
                temporary = path.with_suffix(path.suffix + ".part")
                temporary.write_bytes(data)
                temporary.replace(path)
                path.with_suffix(path.suffix + ".headers.json").write_text(json.dumps(dict(response.headers), indent=2))
            return
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2)



def rings(geometry):
    """Extract polygon boundary coordinates for vector rendering."""
    if ogr.GT_Flatten(geometry.GetGeometryType()) == ogr.wkbLinearRing or geometry.GetGeometryName() in ["LINEARRING", "LINESTRING"]:
        return [np.array(geometry.GetPoints())[:, :2]]
    return [line for child in geometry for line in rings(child)]


def _parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="ref/huc/config.yml")
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = _parse_arguments()
    main_build_huc(args.config)
