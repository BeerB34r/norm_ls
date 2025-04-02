vim.lsp.config['norm_ls'] = {
	cmd = { "python3", "/path/to/norm_ls.py" },
	filetypes = { "c" },
	single_file_support = true,
}
vim.lsp.enable('norm_ls')
