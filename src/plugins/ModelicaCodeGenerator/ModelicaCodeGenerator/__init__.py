"""
This is where the implementation of the plugin code goes.
The ModelicaCodeGenerator-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
import json
import os
import random
import shutil
from webgme_bindings import PluginBase
from mako.template import Template

# Setup a logger
logger = logging.getLogger('ModelicaCodeGenerator')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


# prepare the templates
# modelica_code_template = Template(filename=os.path.join(os.path.dirname(__file__), 'modelica_tmpl.txt'))
# omc_script_template = Template(filename=os.path.join(os.path.dirname(__file__), 'omc_tmpl.txt'))


class ModelicaCodeGenerator(PluginBase):
    def main(self):
        core = self.core
        META = self.META
        root_node = self.root_node
        active_node = self.active_node
        
        nodes = core.load_sub_tree(active_node)
        path2node = {}
        raw_connectors = []
        template_parameters = {'name': core.get_attribute(active_node,'name'), 'Place':[], 'Transition':[],'InplaceArc':[],'OutplaceArc':[]}

        # collect component and connector data
        for node in nodes:
            path2node[core.get_path(node)] = node
            if core.is_type_of(node,META['Place']):
                #gather its attributes in a name-value dictionary
                node_data = {}
                node_data['name'] = core.get_attribute(node, 'name')
                #node_data['Id'] = core.get_attribute(node, 'nodePath')
                node_data['path'] = core.get_path(node)
                node_data['marking'] = core.get_attribute(node, 'marking')
                template_parameters['Place'].append(node_data)
                
            elif core.is_type_of(node, META['Transition']):
                #gather the source and destination of the pointer
                node_data = {}
                node_data['name'] = core.get_attribute(node, 'name')
                #node_data['Id'] = core.get_attribute(node, 'nodePath')
                node_data['path'] = core.get_path(node)
                template_parameters['Transition'].append(node_data)


            elif core.is_type_of(node, META['InplaceArc']):
                node_data = {}
                node_data['name'] = core.get_attribute(node, 'name')
                #node_data['Id'] = core.get_attribute(node, 'nodePath')
                node_data['path'] = core.get_path(node)
                node_data['src'] = core.get_pointer_path(node, 'src')
                node_data['dst'] = core.get_pointer_path(node, 'dst')
                if node_data['src'] and node_data['dst']:
                    template_parameters['InplaceArc'].append(node_data)

            elif core.is_type_of(node, META['OutplaceArc']):
                node_data = {}
                node_data['path'] = core.get_path(node)
                node_data['name'] = core.get_attribute(node, 'name')
                #node_data['Id'] = core.get_attribute(node, 'nodePath')
                node_data['src'] = core.get_pointer_path(node, 'src')
                node_data['dst'] = core.get_pointer_path(node, 'dst')
                if node_data['src'] and node_data['dst']:
                    template_parameters['OutplaceArc'].append(node_data)

        # The dict for Trainsition and Arcs
        Inplace_Transition_Adjacent = {}
        Outplace_Transition_Adjacent = {}

        # creat the Inplace dict
        for transition in template_parameters['Transition']:
            Inplace_Transition_Adjacent[transition['path']] = []

        for inplacearc in template_parameters['InplaceArc']:
            for transition in template_parameters['Transition']:
                if inplacearc['dst'] == transition['path']:
                    Inplace_Transition_Adjacent[transition['path']].append(inplacearc['src'])
        
        for transition in template_parameters['Transition']:
            Inplace_Transition_Adjacent[transition['path']].sort()

        # creat the Outplace dict
        for transition in template_parameters['Transition']:
            Outplace_Transition_Adjacent[transition['path']] = []

        for outplacearc in template_parameters['OutplaceArc']:
            for transition in template_parameters['Transition']:
                if outplacearc['src'] == transition['path']:
                    Outplace_Transition_Adjacent[transition['path']].append(outplacearc['dst'])
        
        for transition in template_parameters['Transition']:
            Outplace_Transition_Adjacent[transition['path']].sort()


        # The dict for Places and Arcs
        Inplace_Place_Adjacent = {}
        Outplace_Place_Adjacent = {}

        

        # creat the Inplace dict
        for place in template_parameters['Place']:
            Inplace_Place_Adjacent[place['path']] = []

        for inplacearc in template_parameters['InplaceArc']:
            for place in template_parameters['Place']:
                if inplacearc['src'] == place['path']:
                    Inplace_Place_Adjacent[place['path']].append(inplacearc['dst'])
        
        for place in template_parameters['Place']:
            Inplace_Place_Adjacent[place['path']].sort()

        # creat the Outplace dict
        for place in template_parameters['Place']:
            Outplace_Place_Adjacent[place['path']] = []

        for outplacearc in template_parameters['OutplaceArc']:
            for place in template_parameters['Place']:
                if outplacearc['dst'] == place['path']:
                    Outplace_Place_Adjacent[place['path']].append(outplacearc['src'])
        
        for place in template_parameters['Place']:
            Outplace_Place_Adjacent[place['path']].sort()

        IsFreeChoice = 0
        IsStateMachine = 0
        IsMarkedGraph = 0
        IsWorkflow = 0

        # check whether it is FreeChoice
        count = 0
        for transition1 in template_parameters['Transition']:
            for transition2 in template_parameters['Transition']:
                if transition1['path'] != transition2['path']:
                    if Inplace_Transition_Adjacent[transition1['path']] == Inplace_Transition_Adjacent[transition2['path']]:
                        count = count + 1

        if count > 0:
            IsFreeChoice = 0
        else:
            IsFreeChoice = 1
        
        with open('Test.txt','w') as f:
            f.write(str(Inplace_Transition_Adjacent))

        # check whether it is StateMachine
        count = 0
        for transition in template_parameters['Transition']:
            if (len(Inplace_Transition_Adjacent[transition['path']]) != 1) or (len(Outplace_Transition_Adjacent[transition['path']]) != 1):
                count = count + 1

        if count > 0:
            IsStateMachine = 0
        else:
            IsStateMachine = 1
        
        # check whether it is MarkedGraph
        count = 0
        for place in template_parameters['Place']:
            if (len(Inplace_Place_Adjacent[place['path']]) != 1) or (len(Outplace_Place_Adjacent[place['path']]) != 1):
                count = count + 1

        if count > 0:
            IsMarkedGraph = 0
        else:
            IsMarkedGraph = 1

        # check whether it is IsWorkflow
        count_place_in = 0
        count_place_out = 0
        count_transition_in = 0
        count_transition_out = 0
        for place in template_parameters['Place']:
            if (len(Inplace_Place_Adjacent[place['path']]) == 0):
                count_place_in = count_place_in + 1
            if (len(Outplace_Place_Adjacent[place['path']]) == 0):
                count_place_out = count_place_out + 1

        for transition in template_parameters['Transition']:
            if (len(Inplace_Transition_Adjacent[transition['path']]) == 0):
                count_transition_in = count_transition_in + 1
            if (len(Outplace_Transition_Adjacent[transition['path']]) == 0):
                count_transition_out = count_transition_in + 1

        if count_place_in == 1 and count_place_out == 1 and count_transition_in == 0 and count_transition_out == 0:
            IsWorkflow = 1
        else:
            IsWorkflow = 0

        classification = str(IsFreeChoice) + ',' + str(IsStateMachine) + ',' + str(IsMarkedGraph) + ',' + str(IsWorkflow)

        messages = []
        
        # send notification and create messages
        for place in template_parameters['Place']:
            message = 'Place,' + place['name'] + ',' + place['path'] + ',' + str(place['marking'])
            self.create_message(active_node, str(message), severity= 'info')
            messages.append(message)
        for transition in template_parameters['Transition']:
            message = 'Transition,' + transition['name'] + ',' + transition['path']
            self.create_message(active_node, str(message), severity= 'info')
            messages.append(message)
        for inplacearc in template_parameters['InplaceArc']:
            message = 'InplaceArc,' + inplacearc['name'] + ',' + inplacearc['path'] + ',' + inplacearc['src'] + ','  + inplacearc['dst']
            self.create_message(active_node, str(message), severity= 'info')
            messages.append(message)
        for outplacearc in template_parameters['OutplaceArc']:
            message = 'OutplaceArc,' + outplacearc['name'] + ',' + outplacearc['path'] + ',' + outplacearc['src'] + ',' + outplacearc['dst']
            self.create_message(active_node, str(message), severity= 'info')
            messages.append(message)

        self.create_message(active_node, classification, severity= 'info')


        # You can use txt to check your results
        with open('classification.txt','w') as f:
            f.write(str(classification))
        

        # render templates
        # modelica_code = modelica_code_template.render(name = template_parameters['name'], connectors = template_parameters['connectors'], components = template_parameters['components'])
        # omc_script = omc_script_template.render(name = template_parameters['name'], stop_time = 1.0)

        # #put content into temporary directory
        # directory_name = 'mod_sim_'
        # for i in range(10):
        #     diectory_name += str(random.randint(0,9))
        # directory = os.path.join(os.path.dirname(__file__), directory_name)
        # os.mkdir(directory)
        # os.chdir(directory)
        # model_file = open(template_parameters['name'] + '.mo', 'w+')
        # model_file.write(modelica_code)
        # model_file.close()
        # omc_file = open('simulate.mos','w+')
        # omc_file.write(omc_script)
        # omc_file.close()

        # #run simulation
        # os.system('omc simulate.mos')

        # #pre-process result
        # result_file = open(template_parameters['name'] + '_res.csv', 'r')
        # result = result_file.readlines()
        # result_file.close()

        # result_list = []
        # for line in result:
        #     result_list.append(line.split(','))
        # size = len(result_list[0])
        # processed_result = {}
        # index_helper = {}
        # for idx, column in enumerate(result_list[0]):
        #     processed_result[column.replace('"','')] = []
        #     index_helper[idx] = column.replace('"','')
        # result_list = result_list[1:]
        # for list in result_list:
        #     for idx, value in enumerate(list):
        #         processed_result[index_helper[idx]].append(value)


        # #save result into model
        # core.set_attribute(active_node, 'simRes', str(json.dumps(processed_result)))

        # #runserversplugin
        # # message = self.create_message(active_node, 'message')
        # # #notification = self.send_notification('helloTxT, %s' % message)

        # # self.createMessage(message,'Hello','info')


        # #commit changes
        # self.util.save(root_node, self.commit_hash, self.branch_name, 'Simulation result saved into model.')

        # #clean up temporary diretory
        # os.chdir("..")
        # shutil.rmtree(directory)