# -*- coding:utf8 -*-
import xml.etree.ElementTree as ET
import config
from xml.dom import minidom


def generateRoot():
    root = ET.Element('bpmn:definitions')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xmlns:bpmn', 'http://www.omg.org/spec/BPMN/20100524/MODEL')
    root.set('xmlns:bpmndi', 'http://www.omg.org/spec/BPMN/20100524/DI')
    root.set('xmlns:dc', 'http://www.omg.org/spec/DD/20100524/DC')
    root.set('xmlns:di', 'http://www.omg.org/spec/DD/20100524/DI')
    root.set('targetNamespace', 'http://bpmn.io/schema/bpmn')
    root.set('id', 'Definitions_1')
    return root


def saveXML(root, filename, indent="\t", newl="\n", encoding="utf-8"):
    rawText = ET.tostring(root)
    dom = minidom.parseString(rawText)
    with open(filename, 'w') as f:
        dom.writexml(f, "", indent, newl, encoding)


def generateProcess(root, node_diclist, connections_graph):
    sequencelist = []
    process = ET.SubElement(root, 'bpmn:process')
    process.set('id', 'Process_1')
    process.set('isExecutable', 'false')
    for node in node_diclist:
        for key in node.keys():
            node[key] = generateTask(key, process)
    order = 0
    for con in connections_graph:
        sequencename = generateSequence(con, process, order)
        order += 1
        sequencelist.append(sequencename)
    return sequencelist


def generateTask(key, process):
    task = ET.SubElement(process, 'bpmn:task')
    task.set('id', 'Task_'+key)
    task.set('name', key)
    return task


def generateSequence(con, process, order):
    a, b, direct = con
    sequence = ET.SubElement(process, 'bpmn:sequenceFlow')
    sequencename = 'SequenceFlow_'+str(order)
    sequence.set('id', sequencename)
    for task in root.iter('bpmn:task'):
        if task.attrib.get('name') == a:
            outgoing = ET.SubElement(task, 'bpmn:outgoing')
            outgoing.text = sequencename
            sequence.set('sourceRef', task.attrib.get('id'))
        elif task.attrib.get('name') == b:
            incoming = ET.SubElement(task, 'bpmn:incoming')
            incoming.text = sequencename
            sequence.set('targetRef', task.attrib.get('id'))
    return sequence


def generateDiagram(root):
    diagram = ET.SubElement(root, 'bpmndi:BPMNDiagram')
    diagram.set('id', 'BPMNDiagram_1')
    plane = ET.SubElement(diagram, 'bpmndi:BPMNPlane')
    plane.set('id', 'BPMNPlane_1')
    plane.set('bpmnElement', 'Process_1')
    return plane


def generateShape(plane, node_diclist):
    nodelist = {}
    level = 0
    for node in node_diclist:
        length = len(node)
        start_x = 0
        if length % 2 == 0:
            start_x = config.begin_x - \
                (config.width+config.w_distance)*(length/2)
        else:
            start_x = config.begin_x - \
                (config.width+config.w_distance)*((length-1)/2)-config.width/2
        number = 0
        for key, value in node.items():
            shape = ET.SubElement(plane, 'bpmndi:BPMNShape')
            task_id = value.attrib.get('id')
            shape.set('bpmnElement', task_id)
            shape.set('id', task_id+"_di")
            bounds = ET.SubElement(shape, 'dc:Bounds')
            bounds.set('height', str(config.height))
            bounds.set('width', str(config.width))
            bounds.set(
                'x', str(start_x+(config.width+config.w_distance)*number))
            bounds.set('y', str(config.begin_y+level*config.h_distance))
            nodelist[key] = [bounds.attrib.get('x'), bounds.attrib.get('y')]
            number += 1
        level += 1
    return nodelist


def generateEdge(plane, connections_graph, nodelist, sequencelist):
    number = 0
    for con in connections_graph:
        a, b, direct = con
        edge = ET.SubElement(plane, 'bpmndi:BPMNEdge')
        sequenceid = sequencelist[number].attrib.get('id')
        edge.set('bpmnElement', sequenceid)
        edge.set('id', sequenceid+"_di")
        start = ET.SubElement(edge, 'di:waypoint')
        to = ET.SubElement(edge, 'di:waypoint')
        a_x, a_y = nodelist.get(a)
        b_x, b_y = nodelist.get(b)
        start.set('x', str(float(a_x)+config.width/2))
        start.set('y', str(float(a_y)+config.height))
        to.set('x', str(float(b_x)+config.width/2))
        to.set('y', b_y)
        number += 1


if __name__ == '__main__':
    # 初始化数据 a->b a->c
    node_diclist = [{'设备a': ''}, {'设备b': '', '设备c': '','设备d':''},{'设备e':'','设备f':''}]
    connections_graph = [['设备a', '设备b', 1], ['设备a', '设备c', 1],['设备a', '设备d', 1],['设备d', '设备e', 1],['设备b', '设备f', 1]]
    root = generateRoot()
    sequencelist = generateProcess(root, node_diclist, connections_graph)
    plane = generateDiagram(root)
    nodelist = generateShape(plane, node_diclist)
    generateEdge(plane, connections_graph, nodelist, sequencelist)
    saveXML(root, "note.xml")
