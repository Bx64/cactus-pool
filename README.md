# Dashboard for [cactus-tbw](https://github.com/Cactus-15-49/cactus-tbw) Solar Core plugin 

## Prerequisites

1. Install pip and python3.6 or above

2. Install `pm2`

```bash
npm install pm2@latest -g
# or
yarn global add pm2
```

## Clean / New Installation

```sh
# Install and sync relay server + install and configure cactus-tbw core plugin
# See respective repositories for instructions on those installations
# After you finish setting up your server and plugin, continue.

# Clone cactus-pool repository
git clone https://github.com/Bx64/cactus-pool && cd ~/cactus-pool

# Install requirements
pip3 install -r requirements.txt

# Clone pool config example
cp ~/cactus-pool/core/config/pool_config.ini.example ~/cactus-pool/core/config/pool_config.ini

# Fill out config (see below)
nano ~/cactus-pool/core/config/pool_config.ini

# With your cactus-tbw core plugin fully synced, run the first pending balances check manually (only required for initialisation!)
cd ~/cactus-pool/core && python3 poolinit.py

# Start the dashboard with pm2
cd ~/cactus-pool/core && pm2 start pool.json

# Congratulations! Your pool dashboard will now automatically update the pending balances every 10 minutes.
```

## Configuration & Usage

1. After the repository has been cloned you need to open the [config](./core/config/pool_config.ini) and change it to your liking (see [Available Configuration Options](#available-configuration-options)). Below is the example config. You need to update the values of `network`, `username`, `delegate` and the values of the items under `[pool]`.

```
[static]
atomic = 100000000
network = testnet
username = username

[delegate]
delegate = delegate

[pool]
pool_ip = xx.xx.xx.xx
pool_port = 5000
pool_template = bfx
explorer = https://texplorer.solar.org
coin = tSXP
proposal1 = https://delegates.solar.org/delegates/xxxx
proposal2 = https://yy.yy.yy
proposal2_lang = CC

[logging]
loglevel = INFO
formatter = %(levelname)s %(message)s
```

Python 3.6+ is required.


## Available Configuration Options 

### [static]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| atomic | 100000000 | Atomic value - **do not change** |
| network | testnet | testnet or mainnet |
| username | username | Operating system username |

### [delegate]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| delegate | delegate | Delegate name |

### [pool]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| pool_ip | xx.xx.xx.xx | IP of the node the pool is installed on |
| pool_port | 5000 | Port for pool |
| pool_template | bfx | Set the pool website template - only option |
| explorer | https://texplorer.solar.org | The address of the explorer for the network |
| coin | tSXP | tSXP or SXP |
| proposal1 | https://delegates.solar.org/delegates/xxxx | Link to delegate proposal |
| proposal2 | https://yy.yy.yy | Link to the proposal in different language |
| proposal2_lang | CC | Language (code) of the second proposal |

### [logging]
| Option | Default Setting | Description | 
| :--- | :---: | :--- |
| loglevel | INFO | Can be turned to DEBUG in order to have full debug outputs |
| formatter | %(levelname)s %(message)s | Log formatter |


## To Do

- TBD

## Changelog

### 0.1.0

- Initial release

## Security

If you discover a security vulnerability within this package, please open an issue. All security vulnerabilities will be promptly addressed.

## Credits

- [bfx](https://delegates.solar.org/delegates/bfx) ([Bx64](https://github.com/Bx64))
- [galperins4](https://github.com/galperins4)
- [All Contributors](../../contributors)

## License

[MIT](LICENSE) ?? [galperins4](https://github.com/galperins4)
