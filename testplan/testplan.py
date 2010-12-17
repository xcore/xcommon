from docutils import nodes
from docutils.core import publish_parts
from docutils.parsers.rst import Directive, directives
import sys, string
import docutils.io
from docutils.parsers.rst import directives
from docutils import core
import docutils
from docutils.frontend import OptionParser
import StringIO
import sys, re

if sys.version_info < (2,6):
    from sets import Set as set


def pattern_filter(pattern, xs, report_failed=None, check_errors=False,
                   range_match=False):
    ps = pattern.split(",")
    filtered_set = set([])
    for p0 in ps:
        p = p0.split("excluding")
        if (len(p) == 1):
            try:
                pstr = p[0].strip()
                p = re.compile(pstr + "$")
            except:
                sys.stderr.write("ERROR:`"+p[0].strip()+"' is not a valid regular expression ") 
                if (report_failed):
                    sys.stderr.write(report_failed)
                sys.stderr.write("\n")
                exit(1)
            found = False
            for item in xs:
                if p.match(str(item)):
                    found = True
                    filtered_set.add((item,0))
                elif range_match:
                    range_pattern = re.compile("(.*)__RANGE$")
                    m = range_pattern.match(str(item))
                    if m:
                        item_root = m.groups(0)[0]
                        item_pattern = re.compile(item_root + "_(.*)")
                        m = item_pattern.match(pstr)
                        if m:                            
                            n = int(m.groups(0)[0])
                            filtered_set.add((item, n))

            if check_errors and report_failed and not found:                    
                sys.stderr.write("Cannot match `" + p0 + "'" + report_failed +"\n")
                if check_errors:
                    exit(1)
                
        else:
            in_pattern = re.compile(p[0].strip())
            exc_pattern = re.compile(p[1].strip())
            in_set = set([])
            exc_set = set([])
            for item in xs:
                if in_pattern.match(str(item)):
                    in_set.add(item)
                if exc_pattern.match(str(item)):
                    exc_set.add(item)
            in_set = in_set - exc_set
            filtered_set = set.union(filtered_set, in_set)
    return list(filtered_set)


def assert_no_empty_lists(name, ll):
    for l in ll:
        if l == []:
            sys.stderr.write("ERROR : empty list found where expected a `"+name+"' item (cross-reference lookup failed?)\n")
#            traceback.print_tb()
            exit(1)
    

def cross(args):
    ans = [[]]
    if (args == [[]]):
        return ans
    #print "cross(" + repr(args) + ")"
    for arg in args:
        ans = [x+[y] for x in ans for y in arg]

    assert ans != [[]]
    return ans


class TestPlanDirective(Directive):

    def make_targetnode(self):
        targetnode = nodes.target('','',ids=[nodes.make_id(self.arguments[0].strip())])
        name = nodes.fully_normalize_name(self.arguments[0].strip())
        targetnode['names'].append(name)
        self.state_machine.document.note_explicit_target(targetnode, targetnode)
        return targetnode

    def options_to_field_list(self, option_map):
        field_list = None
        for option, name in option_map.iteritems():
            if option in self.options:
                

                if (field_list == None):
                    field_list = nodes.field_list()
                option_field = nodes.field()
                option_field_name = nodes.field_name()
                option_field_name += nodes.Text(name)
                option_field += option_field_name
                option_field_body = nodes.field_body()
                option_field += option_field_body;

                # Don't attempt to split integer fields:
                if(type(self.options[option]) != int):
                    l = self.options[option].split(",")

                    if (len(l) > 1):
                        option_field_body += nodes.raw('',' \\ \n\n',format="latex")
                    for item in l:
                        parts = item.split("`")
                        p = nodes.paragraph()
                        is_reference = False
                        for part in parts:
                            if is_reference:
                                n = nodes.emphasis()
                                refid = nodes.make_id(self.arguments[0].strip() + "param"+part)
                                n +=  nodes.reference('',part,
                                                     refid=refid)
                                p += n
                            else:
                                p += nodes.Text(part)
                            is_reference = not is_reference
                        option_field_body += p
    
                field_list += option_field
        return field_list

    def __str__(self):
        return self.name

    def parsed(self, n):
        try:
            self.document.parsed
        except AttributeError:
            self.document.parsed = dict([])
        try:
            return self.document.parsed[n]
        except KeyError:
            self.document.parsed[n] = []
            return self.document.parsed[n]
        
    def check_errors(self):
        try:
            return self.document.check_errors
        except AttributeError:
            return False
        
    
class Feature:
    
    choices = []
    parents = []
    name = ""
    is_config_option = False
    
    def __init__(self, name):
        self.name = name
        self.parents=[]
        
    def __str__(self):
        return self.name



class FeatureDirective(TestPlanDirective, Feature):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'parents':directives.unchanged,
                   'config_options':directives.unchanged,
                   'build':directives.unchanged,
                   'runtime':directives.flag,
                   'summarize':directives.flag,
                   'summarize_options':directives.flag}
    has_content = True

    node_class = nodes.note

    def run(self):
        # Content is optional, so don't raise an error if it's missing...
#        print self.state_machine.document.current_source

        self.document = self.state_machine.document
        self.is_config_option = False

        text = '\n'.join(self.content)
        # Create the admonition node, to be populated by `nested_parse`.

        self.name = self.arguments[0].strip()

        title = self.arguments[0]
        if 'parent' in self.options:
            title += " (" + self.options['parent'] + ")"

        term = nodes.term()
        n = nodes.strong(text=title) 
        term += n
        
        targetnode = self.make_targetnode()

        deflist = nodes.definition_list()
        feature_def = nodes.definition_list_item()
        feature_def += term
        defn = nodes.definition()
        feature_def += defn
        deflist += feature_def
        # Parse the directive contents.
        self.state.nested_parse(self.content, self.content_offset,
                                defn)
        option_map = {}
        option_map['parents'] = 'Parent features'
        option_map['config_options'] = 'Options'
        field_list = self.options_to_field_list(option_map)

        if 'parents' in self.options:
            self.parents = []
            for p in self.options['parents'].split(","):
                found = False
                for f in self.parsed('feature'):
                    if p.strip() == f.name:
                        found = True
                if not found:
                    sys.stderr.write("ERROR: Feature `"+self.name+"' refers to unknown parent `"+p.strip()+"'")
                    if self.check_errors():
                        exit(1)

            for p in self.options['parents'].split(","):
                self.parents.extend([f for f in self.parsed('feature') if p.strip() == f.name])

            ancestors = set(self.parents)
            for p in self.parents:
                ancestors = ancestors | set(p.ancestors)
            self.ancestors = list(ancestors)
        else:
            self.parents = []
            self.ancestors = []

        self.summarize = ('summarize' in self.options)
        
        if 'config_options' in self.options:
            self.choices=[]            
            found_default = False
            optstr = self.options['config_options'].strip()
            p = re.compile("(.*), *default *= *(.*)")
            m = p.match(optstr)
            if m:
                optstr = m.groups(0)[0]
                default = m.groups(0)[1]
            else:
                default = None
            p = re.compile("(.*)\.\.(.*)")
            m = p.match(optstr)
            if m:
                lb = int(m.groups(0)[0])
                ub = int(m.groups(0)[1])
                name = self.name + "__RANGE"
                choice = Feature(name)
                choice.summarize = ('summarize_options' in self.options)
                self.choices.append(choice)
                self.parsed('feature').append(choice)
                choice.is_range = True
                choice.is_config_option = True
                choice.is_default = False
                choice.parents = [self]                
                choice.ancestors = [self]
                choice.ancestors.extend(self.ancestors)
            else:
                for o in self.options['config_options'].split('|'):
                    p = re.compile("(.*) \(default\)")
                    is_default = False
                    name = o.strip()
                    if (p. match(name)):
                        name = p.match(name).groups(0)[0]
                        name = name.strip()
                        is_default = True
                        found_default = True
                    if (name == default):
                        is_default = True
                        found_default = True
                    name = self.name + "_" + name
                    choice = Feature(name)
                    choice.is_range = False
                    choice.is_default = is_default
                    choice.summarize = ('summarize_options' in self.options)
                    self.choices.append(choice)
                    self.parsed('feature').append(choice)
                    choice.is_config_option = True
                    choice.parents = [self]                
                    choice.ancestors = [self]
                    choice.ancestors.extend(self.ancestors)
                if not found_default:
                    self.choices[0].is_default = True
        else:
            self.choices=[]

        if (field_list != None):
            defn += field_list



        self.parsed('feature').append(self)
        return [targetnode, deflist]


class Configuration(TestPlanDirective):
    
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'features':directives.unchanged}
    has_content = True
    
    node_class = nodes.note

    # def features(self):
    #     if 'features' in self.options:
    #         return pattern_filter(self.options['features'], self.parsed('feature'))
    #     else:
    #         return []


    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        self.document = self.state_machine.document

        text = '\n'.join(self.content)
        # Create the admonition node, to be populated by `nested_parse`.

        self.name=self.arguments[0].strip()

        term = nodes.term()
        term += nodes.strong(text=self.arguments[0]) 

        targetnode = self.make_targetnode()

        deflist = nodes.definition_list()
        configuration_def = nodes.definition_list_item()
        configuration_def += term
        defn = nodes.definition()
        configuration_def += defn
        deflist += configuration_def

        # Parse the directive contents.
        self.state.nested_parse(self.content, self.content_offset,
                                defn)
        
        option_map = {}
        option_map['features'] = 'Required for features'
        field_list = self.options_to_field_list(option_map)

        if (field_list != None):
            defn += field_list

        self.parsed('configuration').append(self)
        return [targetnode, deflist]




class TestInstance:
    args = []
    configuration = []
    features = []
    defaults = []
    test = None

    def __init__(self, test, args, configuration, features, defaults):
        self.test = test
        self.args = args
        self.configuration = configuration
        self.features = features
        all_features = set(features)
        for f in features:
            all_features = all_features | set(f.ancestors)

        all_features = all_features | set([c[0] for c in configuration])
        for f in configuration:
            all_features = all_features | set(f[0].ancestors)
        self.all_features = list(all_features)
        self.defaults = defaults

    def __str__(self):
        name = self.test.name
        for c in self.configuration:
            if c[0].is_config_option and c[0].is_range:
                p = re.compile("(.*)__RANGE")
                m = p.match(str(c[0]))
                name += "_" + m.groups(0)[0] + "_" + str(c[1])
            else:
                name += "_" + str(c[0])
        for a in self.args:
            name += "_" + a['param'] + "_" + a['value']
        return name


class Test(TestPlanDirective):
    
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'features':directives.unchanged,
                   'configurations':directives.unchanged,
                   'features':directives.unchanged,
                   'setup':directives.unchanged,
                   'parameters':directives.unchanged,
                   'test_time':directives.nonnegative_int,
                   'test_procedure':directives.unchanged,
                   'priority':directives.nonnegative_int}
    has_content = True
    test_procedure = None
    test_time = 0

    node_class = nodes.note

    num_params = 0

    def split_param(self, param):
        l = param.split("=");
        choices = [s.strip() for s in l[1].split("|")]
        return {'param':l[0].strip(),
                'choices_str':l[1].strip(),
                'choices':choices}

    def parse_parameters(self):
        if 'parameters' in self.options:
            params = self.options['parameters'].split(",")            
            params = [ self.split_param(p) for p in params ]
        else:
            params = []
        return params

    def get_configs(self, pattern):
        for f in [x for x in self.parsed('feature') if x.choices != []]:
            cs = pattern_filter(pattern, f.choices, report_failed=" in test '"+self.name+"'", range_match=True)
            if cs != []:
                return cs
        sys.stderr.write("ERROR: Cannot match configuration pattern `"+pattern+"' in test `" + self.name + "'\n")
        if self.check_errors():
            exit(1)

    def configurations(self,spaces):
        if not 'configurations' in self.options:
            if spaces != []:
                return cross(spaces)
            else:
                return [[]]
            
            
        pattern = self.options['configurations']
        ps = pattern.split("+")
        #print "configurations : ps = " + repr(ps)
        cs = []
        for p in ps:
            xs = p.split(",")            
            #print "configurations : xs = " + repr(xs)
            c = spaces[:]
            for x in xs:
                #print "configurations : x = " + repr(x)
                c.append(self.get_configs(x))
            #print "configurations : c = " + repr(c)                    
            c = cross(c)
            cs.extend(c)
        #print "configurations : cs = " + repr(cs)            
        return cs
 
    def features(self, args):
        if 'features' in self.options:
            feature_str = self.options['features']
            for arg in args:
                feature_str = feature_str.replace("`" + arg['param'] + "`",
                                                      arg['value'])
            features = pattern_filter(feature_str, self.parsed('feature'),
                                      report_failed="in test !`"+self.name+"'",
                                      check_errors=self.check_errors(),
                                      range_match=False)      

            features = [f[0] for f in features]

            if (features == []):
                sys.stderr.write("ERROR: Cannot match feature `" + feature_str + "' in test `" + self.name + "'")
                if (self.check_errors()):
                    exit(1)
        

            #parent_features = set([])
            #for f in features:
            #parent_features = set.union(parent_features, set(f.parents))    

            #features = list(set.union(set(features),parent_features))         
        else:
            features = []
        return features

    def instances(self):
        params = self.parse_parameters()
        #print "instances.params : " + repr(params)
        spaces = [ x['choices'] for x in params ]
        #print "instances.spaces: " + repr(spaces)
        self.num_params = len(params)
        #print "instances.num_params: " + repr(self.num_params)
        l = self.configurations(spaces)                
             
        instances = []
#        print "instances.l: " + repr(l)
        for config in l:
            args=[]
            for i in range(self.num_params):
                args.append({'param':params[i]['param'],
                             'value':config[i]})


            configs = config[self.num_params:]

            xs = [x for x in self.parsed('feature') if x.choices != []]
            
            defaults = []
            for x in xs:                
                found = False
                for c in x.choices:
                    if c in configs:
                        found = True
                if not found:
                    defaults.extend([d for d in x.choices if d.is_default])   

            features = set(self.features(args))
                            
            for c in configs:
                features.add(c[0])
                features = features.union(set(c[0].parents))

            features = list(features)

            instances.append(TestInstance(self, args, configs, features, defaults))

        # If we have a test then there should be at least one instance...
        assert len(instances) > 0

        return instances
                

    def run(self):
        # Tests don't have to have contents now, so check for it but don't assert:
        self.document = self.state_machine.document
        text = []
        if self.content :
            text = '\n'.join(self.content)

        # Create the admonition node, to be populated by `nested_parse`.

        self.name = self.arguments[0]

        if 'test_time' in self.options:
            self.test_time = self.options['test_time']

        # test_procedure name
        #if 'test_procedure' in self.options:
        if 'test_procedure' in self.options:
            self.test_procedure = self.options['test_procedure']
        else:
            self.assert_has_content()        
            proc = TestProcedure(self.name + "_procedure")
            self.test_procedure = proc.name
            if 'setup' in self.options:
                proc.setup = self.options['setup']
            else:
                proc.setup = ""
            proc.content = self.content
            self.parsed('test_procedure').append(proc)
            
            

        term = nodes.term()
        term += nodes.strong(text=self.arguments[0]) 
        
        targetnode = self.make_targetnode()

        deflist = nodes.definition_list()
        test_def = nodes.definition_list_item()
        test_def += term
        defn = nodes.definition()
        test_def += defn
        deflist += test_def


        if 'parameters' in self.options:
            params = self.parse_parameters()
        
            defn += nodes.paragraph(text="Parameters:")
            for param in params:
                name = param['param']
                field_list = nodes.field_list()
                param_field = nodes.field()
                param_field_name = nodes.field_name()
                param_field_name += nodes.Text(name)
                param_field += param_field_name
                param_field_body = nodes.field_body()
                choices_str = param['choices_str']
                if (len(choices_str) < 50):
                    param_field_body += nodes.paragraph(text=choices_str)
                else:
                    choices = param['choices']
                    param_field_body += nodes.raw('',' \\ \n\n',format="latex")
                    for choice in choices:
                        param_field_body += nodes.paragraph(text=choice)
                param_field += param_field_body
                field_list += param_field
                name = self.arguments[0].strip() + "param" + name
                param_target = nodes.target('','',ids=[nodes.make_id(name)])
                name = nodes.fully_normalize_name(name)
                param_target['names'].append(name)
                self.state_machine.document.note_explicit_target(param_target,
                                                                 param_target)
                defn += param_target
                defn += field_list

        # Parse the directive contents.
        self.state.nested_parse(self.content, self.content_offset, defn)

        option_map = {}
        option_map['configurations'] = 'Valid configurations'
        option_map['setup'] = 'Required setup'
        option_map['test_time'] = 'Test time (min)'
        option_map['priority'] = 'Priority'
        option_map['test_procedure'] = 'Test procedure'
        field_list = self.options_to_field_list(option_map)

        if (field_list != None):
            defn += field_list

        self.parsed('test').append(self)
        return [targetnode, deflist]

class TestProcedure:
    
    choices = []
    parents = []
    name = ""
    is_config_option = False
    
    def __init__(self, name):
        self.name = name
        self.parents=[]
        
    def __str__(self):
        return self.name


class TestProcedureDirective(TestPlanDirective, TestProcedure):
    
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'direction':directives.unchanged,
                   'setup':directives.unchanged_required}
    has_content = True
    setup = ""
    direction = 0

#    node_class = nodes.note
#

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        self.document = self.state_machine.document

        text = '\n'.join(self.content)
        # Create the admonition node, to be populated by `nested_parse`.

        self.name = self.arguments[0]
        
        term = nodes.term()
        term += nodes.strong(text=self.arguments[0]) 
        
        targetnode = self.make_targetnode()

        deflist = nodes.definition_list()
        test_def = nodes.definition_list_item()
        test_def += term
        defn = nodes.definition()
        test_def += defn
        deflist += test_def


        # CURRENT : Parse direction list if provided, which is comma-separated
        if 'direction' in self.options:
            input = 0
            output = 0

            for p in self.options['direction'].split(","):
#                print "Testing `" + p.strip() + "' in test_procedure `" + self.name + "'..."

                if p == "input":
                    input = 1
                
                if p == "output":
                    output = 2

            self.direction = input + output


        # Parse the directive contents.
        self.state.nested_parse(self.content, self.content_offset, defn)

        option_map = {}
        option_map['setup'] = 'Required setup'
        option_map['direction'] = 'Direction (input|output|both)'
        field_list = self.options_to_field_list(option_map)

        if (field_list != None):
            defn += field_list

        #print "*** TestProcedure options setup = " + self.options['setup']
        if 'setup' in self.options:
            self.setup = self.options['setup']

        self.parsed('test_procedure').append(self)
        return [targetnode, deflist]


class Setup(TestPlanDirective):
    
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'setup_time':directives.unchanged}
    has_content = True
    setup_time = 0

    node_class = nodes.note

    def run(self):
        # Raise an error if the directive does not have contents.
        self.assert_has_content()
        self.document = self.state_machine.document

        self.name = self.arguments[0]
        #print "*** SETUP RUN HIT!"

        self.setup_time = int(self.options['setup_time'])

        text = '\n'.join(self.content)
        # Create the admonition node, to be populated by `nested_parse`.

        term = nodes.term()
        term += nodes.strong(text=self.arguments[0]) 

        targetnode = self.make_targetnode()

        deflist = nodes.definition_list()
        behaviour_def = nodes.definition_list_item()
        behaviour_def += term
        defn = nodes.definition()
        behaviour_def += defn
        deflist += behaviour_def

        # Parse the directive contents.
        self.state.nested_parse(self.content, self.content_offset, defn)
        
        option_map = {}
        option_map['setup_time'] = 'Setup time'
        field_list = self.options_to_field_list(option_map)

        if (field_list != None):
            defn += field_list

        #print "*** self.parsed('setup').append(self)!"
        self.parsed('setup').append(self)
        return [targetnode, deflist]


class PrepareSetup(TestPlanDirective):
    
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'runtests':directives.unchanged_required,
                   'setup':directives.unchanged_required}
    has_content = False
    runtests = []

    node_class = nodes.note


    def run(self):
        #self.assert_has_content()
        self.document = self.state_machine.document
        #text = '\n'.join(self.content)
        # Create the admonition node, to be populated by `nested_parse`.

        self.name = self.arguments[0]
        
        term = nodes.term()
        term += nodes.strong(text=self.arguments[0]) 
        
        targetnode = self.make_targetnode()

        deflist = nodes.definition_list()
        test_def = nodes.definition_list_item()
        test_def += term
        defn = nodes.definition()
        test_def += defn
        deflist += test_def

        # Parse the directive contents.
        self.state.nested_parse(self.content, self.content_offset, defn)

        option_map = {}
        option_map['runtests'] = 'Tests to run'
        field_list = self.options_to_field_list(option_map)

        if 'runtests' in self.options:
            self.runtests = []
            for p in self.options['runtests'].split(","):
#                print "Testing for `" + p.strip() + "' in prepare_setup `" + self.name + "'..."
                newruntests = [t for t in self.parsed('test') if p.strip() == t.name]
                if len(newruntests) == 0:
                    sys.stderr.write("ERROR : runtests field couldn't expand to any tests for name `" + p.strip() + "'\n")
                    if (self.check_errors()):
                        exit(1)

#                for t in newruntests :
#                    print "Runtests adding test : " + t.name
    
                self.runtests.extend(newruntests)

        else:
            self.runtests = []

        if (field_list != None):
            defn += field_list

        self.parsed('prepare_setup').append(self)
        return [targetnode, deflist]


    

def register_testplan_directives():
    directives.register_directive("feature", FeatureDirective)
    directives.register_directive("configuration", Configuration)
    directives.register_directive("test", Test)
    directives.register_directive("setup", Setup)
    directives.register_directive("test_procedure", TestProcedureDirective)
    directives.register_directive("prepare_setup", PrepareSetup)

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass


def parse_testplan(source, parsed, is_spec,check_errors=False):
    register_testplan_directives()
    oldstderr = sys.stderr
    docutils_out = StringIO.StringIO()
#    sys.stderr = docutils_out    
    valid = True
    reader_class=docutils.readers.get_reader_class("standalone")
    reader=reader_class(None,"rst")
    option_parser = OptionParser(
        components=(reader.parser, reader),
        defaults=[], read_config_files=1,
        usage="", description="")
    settings = option_parser.get_default_values()
#    try:
    reader.source = source
    reader.settings = settings
    reader.input = reader.source.read()
    reader.document = doc = reader.new_document()
    doc.parsed = parsed
    doc.check_errors = check_errors
    reader.parser.parse(reader.input, doc)
    doc.current_source = doc.current_line = None
    parsed = doc.parsed
#    except:
#        valid = False
#        parsed = None
    sys.stderr = oldstderr    
    err_msg = docutils_out.getvalue()
    
    if 'feature' in parsed:
        for f in parsed['feature']:
            try:
                f.from_spec
            except:
                f.from_spec = is_spec

    return (valid and err_msg.find("ERROR") == -1), err_msg, parsed

def parse_testplan_file(file_name, parsed={}, is_spec=False,check_errors=False):
    source = docutils.io.FileInput(open(file_name),source_path=file_name)
    return parse_testplan(source, parsed, is_spec, check_errors=check_errors)

def parse_testplan_string(string, parsed={}, is_spec=False, check_errors=False):
    source = docutils.io.StringInput(string)
    return parse_testplan(source, parsed, is_spec, check_errors=check_errors)
    
def testplan_string_to_html(string):
    register_testplan_directives()
    parts = publish_parts(source=string, writer_name="html4css1", settings_overrides=[])
    return parts["fragment"]


def complete_parsed(parsed):
    for x in ['feature','configuration','behaviour','test','test_procedure','setup','prepare_setup']: 
        if not x in parsed:
            parsed[x] = []
    return parsed
