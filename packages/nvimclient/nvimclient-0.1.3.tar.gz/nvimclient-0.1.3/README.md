# nvimclient
Open new file in existing neovim instance, worked on both windows and linux, powered by pynvim.

# Requires
Python >= 3.7
pynvim >= 0.4.3

# Install
```bash
pip install nvimclient
```

# Usage
First, you need to set `NVIM_LISTEN_ADDRESS` in system environment(or you can provide server address by -s parameters):
```bash
NVIM_LISTEN_ADDRESS='\\.\pipe\nvim-pipe-12345'
```
Then, you can use nvc to open new file in exist nvim instance:
```bash
nvc foo.txt # if instance not exist, open in command line
nvc foo.txt -g nvim-qt # if instance not exist, open in nvim-qt
```
