from configparser import ConfigParser

#read config
_cfg = ConfigParser()
_cfg.read('pp_config.ini', encoding='utf_8')

def section(sec):
    return _cfg[sec] if sec in _cfg.sections() else None 

def value(sec, key):
    return _cfg[sec][key] if section(sec) and key in section(sec) else None 
            
    