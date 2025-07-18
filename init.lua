vim.lsp.config['norm_ls'] = {
	cmd = { "/path/to/norm_ls.py" },
	filetypes = { "c" },
	single_file_support = true,
}
vim.lsp.enable('norm_ls')
