local M = {}

M.setup = function()
  -- nothing yet
end

M.get_char = function()
  local cursor = vim.fn.getpos(".")
  local line = vim.api.nvim_get_current_line()
  -- local text = vim.api.nvim_buf_get_text(cursor[1], cursor[2]-1, cursor[3]-1, cursor[2]-1, cursor[3],{})
  local text = vim.fn.strpart(line, cursor[3] - 1, 1, 0)
  return (text)
end

local utf8charinfo = function(byte)
  if byte >= 0 and byte <= 127 then
    return 1
  elseif byte >= 192 and byte <= 223 then
    return 2
  elseif byte >= 224 and byte <= 239 then
    return 3
  elseif byte >= 240 and byte <= 247 then
    return 4
  else
    return 1      -- Valeur par défaut en cas d'octet invalide
  end
end

M.get_sentence_node = function()
  local node = vim.treesitter.get_node()
  while node:type() ~= "tree" do
    node = node:parent()
  end
  local a, _, c, _ = node:range()
  local lines = vim.api.nvim_buf_get_lines(0,a, c+1, false)
  local conll_str = table.concat(lines, "\n")
  return conll_str
end


M.get_last_selection = function()
  local start = vim.fn.getpos("'<")
  local stop = vim.fn.getpos("'>")
  local lines = vim.api.nvim_buf_get_lines(0, start[2] - 1, stop[2], false)
  local end_char = vim.fn.strpart(lines[#lines],stop[3] - 1, 1,1)
  local end_pos = stop[3]
  if string.len(lines[#lines]) > 0 then
    end_pos = end_pos + utf8charinfo(string.byte(end_char))
  end
  if #lines == 1 then
    lines[#lines] = string.sub(lines[#lines],start[3], end_pos - 1)
  else
    lines[1] = string.sub(lines[1],start[3])
    lines[#lines] = string.sub(lines[#lines],1, end_pos -1)
  end
  return table.concat(lines, "\n")
end



local split = function(str)
  local result = {}
  for l in string.gmatch(str, "[^\n]+") do
    table.insert(result,l)
  end
  return result
end



local render_tree = function(conllu_str)
  local src = debug.getinfo(1)['source']
  local dir = string.sub(src,2, string.len("/lua/conllu.lua")* -1)
  local result = vim.fn.system('echo "'..conllu_str..'" | python3 '..dir..'rplugin/python3/conll.py')
  return result
end



local new_win = function(text)

  local buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_lines(buf, 0, -1, false, split(text))
  -- vim.api.nvim_buf_set_text(buf,0,0,0,0,split(output))
  local win_config = {
    split = "below",
  }
  vim.api.nvim_open_win(buf, false, win_config)
end

local function create_floating_window(opts, text)
  opts = opts or {}
  local width = opts.width or math.floor(vim.o.columns * 0.8)
  local height = opts.height or math.floor(vim.o.lines * 0.8)

  local col = math.floor((vim.o.columns - width) / 2)
  local row = math.floor((vim.o.lines - height) / 2)

  local buf = vim.api.nvim_create_buf(false, true)

  vim.api.nvim_buf_set_lines(buf, 0, -1, false, split(text))
  local win_config = {
    relative = "editor",
    width = width,
    height = height,
    col = col,
    row = row,
    style = "minimal",
    border = "rounded",
  }

  local win = vim.api.nvim_open_win(buf, true, win_config)

  return { buf = buf, win = win }
end
vim.api.nvim_create_user_command("ViewTree",
  function ()
    local selection = M.get_sentence_node()
    local tree = render_tree(selection)
    new_win(tree)
    --create_floating_window({}, tree)
  end,{})

vim.keymap.set({"n"},"tt", ":ViewTree<CR>")

return M
