local json = require('json')
local norm_ls = {}

function norm_ls.format_error(error)
	return {
		range = {
			start = {
				line = error.line - 1,
				char = error.char - 1,
			},
			["end"] = {
			line = error.line,
			char = error.char,
			},
			severity = 1,
			code = error.code,
			codeDescription = error.message,
			source = "norm_ls",
			message = error.code,
		}
	}
end


--- capture the output of a command into a string
---@param cmd string command to be ran
---@param raw boolean wether to process output or not
---@return string s output of command
function os.capture(cmd, raw)
	local f = assert(io.popen(cmd, 'r'))
	local s = assert(f:read('*a'))
	f:close()
	if raw then return s end
	s = string.gsub(s, '^%s+', '')
	s = string.gsub(s, '%s+$' , '')
	s = string.gsub(s, '[\n\r]+', '')
	return s
end

function norm_ls.get_errors(file)
	local lines = os.capture("norminette " .. file , true):gmatch("Error: [^\n]+")
	local errors = {}

	for line in lines do
		table.insert(errors, {
			code = line:match("Error:%s*[%u_]+"):match("[%u_]+", 2),
			line = line:match("line:%s*%d+"):match("%d+"),
			char = line:match("col:%s*%d+"):match("%d+"),
			message = line:match("%):.*"):match("%u[%a%s]+")
		})
	end
	return errors
end

function norm_ls.get_diagnostics(file)
	local errors = norm_ls.get_errors(file)
	local diagnostics = {}

	for _,v in pairs(errors) do
		table.insert(diagnostics, norm_ls.format_error(v))
	end
	return diagnostics
end

function norm_ls.publish_diagnostics(diagnostics, file)
	local body = json.encode{
		jsonrpc = "2.0",
		method = "textDocument/publishDiagnostics",
		params = {
			uri = file,
			diagnostics = diagnostics
		}
	}
	io.write("Content-Length: " .. #body .. "\r\n\r\n" .. body)
	io.flush()
end

function norm_ls.publish_capabilities(id)
	local body = json.encode({
		jsonrpc = "2.0",
		id = id,
		result = {
			capabilities = {
				textDocumentSync = {
					{ openClose = true },
					{ change = 1 },
					{ save = { includeText = false } },
				},
				diagnosticProvider = {
					{ interFileDependencies = false },
					{ workspaceDiagnostics = false },
				}
			}
		}
	})
	io.write("Content-Length: " .. #body .. "\r\n\r\n" .. body)
	io.flush()
end

function norm_ls.read_input()
	local headers = {}
	while true do
		local line = io.read("*l")
		if not line then return nil end
		if line == "" then break end
		local name, value = line:match("^(.-):%s*(.+)$")
		if name then headers[name:lower()] = value else return nil end
	end

	local content_length = tonumber(headers["content-length"]) or 0
	if not content_length or content_length < 0 then
		return nil
	end

	local body = io.read(content_length)
	if not body or #body ~= content_length then return nil end

	return json.decode(body)
end

function norm_ls.handle_request(request)
	if request.method == "initialize" then
		norm_ls.publish_capabilities(request.id)
	elseif request.method == "textDocument/didOpen" or request.method == "textDocument/didChange" or request.method == "textDocument/didSave" then
		norm_ls.publish_diagnostics(norm_ls.get_diagnostics(request.file), request.file)
	end
end

while true do 
	local request = norm_ls.read_input()
	if request then
		norm_ls.handle_request(request)
	end
end
