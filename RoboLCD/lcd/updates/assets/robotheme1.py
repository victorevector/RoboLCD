import yaml

def get_config(path):
    f = open(path, 'r')
    config = yaml.load(f)
    f.close()
    return config

def write_to_file(config, path):
    f = open(path, 'w')
    yaml.dump(config, f, default_flow_style=False)
    f.close()

def main():
    path = '/home/pi/.octoprint/config.yaml'
    config = get_config(path)
    del config['plugins']['softwareupdate']['checks']['robotheme']
    write_to_file(config, path)
    quit()

if __name__ == '__main__':
    main()
