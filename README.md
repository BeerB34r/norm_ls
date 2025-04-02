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
python, pygls, ill figure the versions in a moment
and norminette of course ;P

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

Vim
```vimscript
insert example config here (can vim even support lsp????)
```

VSCode
```ts
insert example config here
```


