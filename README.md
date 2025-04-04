# norm_ls
### norminette in the background
i got tired of having to run norminette manually and move back and forth between
editor and terminal and checking the numbers myself, so i made this little
thing. now you can have it as diagnostics instead, allowing you to have it as
virtual lines, virtual text or just show up in your error list, whatever you've
configured in your editor of choice


## features
on save, change and open returns the output of norminette in the form of
diagnostic information to your editor
## requirements
python 3.8 or higher (tested on 3.10.12 && 3.9.21)
pygls 2.0.0a2 or higher (tested 2.0.0a1, failed)
```sh
python3 -m pip install "pygls==2.0.0a2"
```
and [norminette](https://github.com/42school/norminette) of course ;P

## installation
I personally use neovim, so take the other installation instruction with a grain
of salt. if you've gotten it to work on your editor, feel free to create a pull
request!

Neovim - init.lua
```lua
vim.lsp.config['norm_ls'] = {
	cmd = { "python3", "/path/to/norm_ls.py" },
	filetypes = { "c" },
	single_file_support = true,
}
vim.lsp.enable('norm_ls')
```
if you are using nvim-lspconfig, put this into the config function instead
```lua
require("lspconfig.configs").norm_ls = {
	cmd = { "python3", "/path/to/norm_ls.py" },
	filetypes = { "c" },
	single_file_support = true,
}
require("lspconfig").norm_ls.setup {}
```

For you VSCode users, there is a plugin with the identifier
`matsdebeer.norm-ls`, heres a [link!](https://marketplace.visualstudio.com/items?itemName=MatsdeBeer.norm-ls)
