Neovim plugin to edit and vizualize CONLLU files
(used by https://universaldependencies.org/ and https://surfacesyntacticud.org/ projects)

It relies on my conllu tree-sitter grammar (https://github.com/pmagistry/tree-sitter-conllu)

These installation instructions assumes you have a basic install of lazy.nvim (https://lazy.folke.io/installation)

All you need to do is then to add a `~/.config/nvim/lua/plugins/conllu.lua' file with the following content:

```lua
return {
  {
    "pmagistry/conllu.nvim",
    lazy = true,
    ft = "conllu"
  }
}
```

you can then run vim, and install this plugin with the `:Lazy` command.
