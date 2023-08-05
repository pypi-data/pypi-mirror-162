import re
import re
import json
import os.path


pkg_dir = os.path.abspath(os.path.dirname(__file__))
default_file = os.path.join(pkg_dir, 'data', 'src', 'user-agents.json')


def compile_pattern(pattern):
    pattern['user_agents'] = [ re.compile(regexp) for regexp in pattern.get('user_agents', []) ]
    return pattern


class Parser:
    def __init__(self, data_file = default_file):
        with open(data_file, 'r') as file:
            data = json.loads(file.read())
            self.patterns = [ compile_pattern(pattern) for pattern in data ]
    
    def parse(self, user_agent):
        """
        >>> parser = Parser()
        >>> parser.parse('AppleCoreMedia/1.0.0.17E262 (iPhone; U; CPU OS 13_4_1 like Mac OS X; zh_tw)')
        {'user_agents': [re.compile('^AppleCoreMedia/1\\\\..*iPhone')], 'app': 'Apple Podcasts', 'device': 'phone', 'examples': ['AppleCoreMedia/1.0.0.15G77 (iPhone; U; CPU OS 11_4_1 like Mac OS X; en_us)'], 'os': 'ios'}
        """
        for pattern in self.patterns:
            user_agents = pattern.get('user_agents', [])
            for user_agent_re in user_agents:
                match = user_agent_re.match(user_agent)
                if match is not None:
                    return pattern


if __name__ == "__main__":
    import doctest
    doctest.testmod()