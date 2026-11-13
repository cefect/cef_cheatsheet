"""Inspect the locally downloaded WBD archive without modifying its geometries."""

import argparse, datetime, hashlib, json, logging, pathlib, time
from osgeo import ogr
import yaml


def main_inspect_wbd(config_path):
    """Record code hierarchy, feature validity, and archive provenance."""
    start = time.monotonic()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    log = logging.getLogger(__name__)
    config = yaml.safe_load(pathlib.Path(config_path).read_text())
    archive = pathlib.Path(config["paths"]["downloads"]) / "WBD_14_HU2_Shape.zip"
    output = pathlib.Path(config["paths"]["build"]) / "wbd_inspection.json"
    log.info(f"Inspecting WBD archive\n    {archive}")
    digest = hashlib.sha256()
    with archive.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    result = {"source": "https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_14_HU2_Shape.zip", "inspected_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "sha256": digest.hexdigest(), "levels": {}}
    parents = set()
    for level in config["levels"]:
        path = f"/vsizip/{archive.resolve()}/Shape/WBDHU{level}.shp"
        source = ogr.Open(path)
        if source is None:
            raise RuntimeError(f"Cannot open {path}")
        layer = source.GetLayer(0)
        codes, invalid, missing_parent = set(), [], []
        for feature in layer:
            code = feature.GetField(f"huc{level}")
            if not isinstance(code, str) or len(code) != level or not code.startswith(config["region"]["code"]) or code in codes:
                raise ValueError(f"Invalid or duplicate HUC{level}: {code}")
            codes.add(code)
            if parents and code[:-2] not in parents:
                missing_parent.append(code)
            geometry = feature.GetGeometryRef()
            if geometry is None or geometry.IsEmpty() or not geometry.IsValid():
                invalid.append(code)
        if not codes:
            raise ValueError(f"Empty HUC{level} layer")
        result["levels"][str(level)] = {"count": len(codes), "invalid_geometries": invalid, "missing_parent_codes": missing_parent, "crs": layer.GetSpatialRef().ExportToWkt(), "extent": layer.GetExtent()}
        parents = codes
        log.info(f"HUC{level}: {len(codes):,} units, {len(invalid):,} invalid geometries, {len(missing_parent):,} missing parents")
    output.write_text(json.dumps(result, indent=2) + "\n")
    log.info(f"Wrote inspection in {time.monotonic() - start:.1f} s\n    {output}")


def _parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="ref/huc/config.yml")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_arguments()
    main_inspect_wbd(args.config)
