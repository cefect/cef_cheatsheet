-- AGENT-001: Keep table notes local and color only HTML pricing tables.
local function has_class(div, class)
  return div.classes:includes(class)
end

local function numeric_value(cell)
  return tonumber((pandoc.utils.stringify(cell.contents):gsub("[$,×%s]", "")))
end

-- Compare positive prices on a log scale within each column and provider.
local function cost_color(value, minimum, maximum)
  local position = 0
  if maximum > minimum then
    position = (math.log(value) - math.log(minimum)) /
      (math.log(maximum) - math.log(minimum))
  end
  local green, yellow, red = {217, 239, 219}, {255, 241, 187}, {246, 204, 204}
  local start, finish, weight = green, yellow, position * 2
  if position > 0.5 then
    start, finish, weight = yellow, red, (position - 0.5) * 2
  end
  local channels = {}
  for i = 1, 3 do
    channels[i] = math.floor(start[i] + (finish[i] - start[i]) * weight + 0.5)
  end
  return string.format("#%02x%02x%02x", table.unpack(channels))
end

local function shade_costs(tbl)
  local rows = {}
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      rows[#rows + 1] = row
    end
  end
  for column = 2, #tbl.colspecs do
    local minimum, maximum = math.huge, 0
    for _, row in ipairs(rows) do
      local value = numeric_value(row.cells[column])
      if value and value > 0 then
        minimum, maximum = math.min(minimum, value), math.max(maximum, value)
      end
    end
    for _, row in ipairs(rows) do
      local cell = row.cells[column]
      local value = numeric_value(cell)
      if value and value > 0 then
        cell.attributes.style = "background-color: " .. cost_color(value, minimum, maximum) ..
          "; color: #202020; box-shadow: none;"
      end
    end
  end
  return tbl
end

function Div(div)
  if FORMAT:match("html") and has_class(div, "cost-table") then
    return div:walk({Table = shade_costs})
  end
  -- Table-specific footnotes stay directly after their table in both formats.
  if FORMAT == "typst" and has_class(div, "table-notes") then
    local blocks = pandoc.List({pandoc.RawBlock("typst", "#block[\n#set text(size: 8pt)\n#set par(leading: 0.35em, spacing: 0.4em)")})
    blocks:extend(div.content)
    blocks:insert(pandoc.RawBlock("typst", "]"))
    return blocks
  end
end
