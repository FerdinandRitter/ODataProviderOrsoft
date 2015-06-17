'''
Created on 29.05.2015

@author: Ferdinand Ritter
'''

import re

# check if LXML is available
try:
    import lxml.etree as xmlstruc
    from lxml import objectify
except ImportError:
    print "Please install LXML!"

VENCODING = "utf-8"

# edmx:Edmx Version="1.0"
EDMX_NS = "http://schemas.microsoft.com/ado/2007/06/edmx"
META_NS = "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"

SCHEMA_NS = "http://schemas.microsoft.com/ado/2008/09/edm"

NS_MAP = {"m": META_NS,
          "edmx": EDMX_NS}


class edmxWriter(object):
    '''
    this class provides functionality to create and handle edmx files, without writing them immediately. therefore some generation, get, delete and a write method is provided
    '''

    '''
    FKN:
    Name:          defines the main name of the data service                     OPTIONAL
    '''
    def __init__(self, ServiceName="DataServices"):

# TODO: version numbers in file header

        # container for the edmx content
        self.root = xmlstruc.Element(xmlstruc.QName(EDMX_NS, 'Edmx'), nsmap=NS_MAP)
        self.root.set("Version", "1.0")
        # direct parent element for the model(s)
        self.top = xmlstruc.SubElement(self.root, xmlstruc.QName(EDMX_NS, ServiceName))
        self.top.set(xmlstruc.QName(META_NS, "DataServiceVersion"), "2.0")
        # default value for current work schema s
        self.schema = None

    '''
    FKN:           returns a new Node VAR "schemaname" with ...
    SName:         defines the specification                                     REQUIRED
    *args:         defines further specification of node                         OPTIONAL
    RETURN:        Object->edmx-schema
    '''
    def addSchema(self, SName, *args):

# TODO: using SCHEMA_NS -> check for other possibilities

        NewSchema = xmlstruc.SubElement(self.top, "Schema", Namespace=SName, nsmap={None : SCHEMA_NS})

        if args:
            try:
                for key, value in args.iteritems():
                    NewSchema.set(key, value)
            except:
# TODO: define exception
                print ""

        if self.schema == None:
            self.schema = NewSchema

        return NewSchema

    '''
    FKN:           change the object attr "schema", if the Arg is an assigned Node and unequal to self.schema
    NewSchema:     Node of self.root/top                                         REQUIRED
    '''
    def changeDefaultSchema(self, NewSchema):

        # if getattr(self.top, NewSchema.tag) and self.schema != NewSchema:
        self.schema = NewSchema

    '''
    FKN:           adds a new Node of namespace "EntityType" to self.schema with at least Name as specification
    Name:          Name of the node                                              REQUIRED
    Schema:        Parent-Element; may be different of current work schema       OPTIONAL
    *args:         further specification of node                                 OPTIONAL
    '''
    def addEntityType(self, ETName, Schema=None, *args):

        if Schema == None:
            Schema = self.schema

        NewNode = xmlstruc.SubElement(Schema, "EntityType", Name=ETName)

        if args:
            try:
                for item in args:
                    for key, value in item.iteritems():
                        NewNode.set(key, value)
            except:
# TODO: define exception
                print "no dict"

    '''
    FKN:           returns an EntityType by Name
    Name:          Name of the node                                              REQUIRED
    Schema:        Parent-Element; may be different of current work schema       OPTIONAL
    RETURN:        Object->edmx-EntityType
    '''
    def getEntityType(self, Name, Schema=None):

        if Schema == None:
            Schema = self.schema

        return Schema.find('.//EntityType[@Name="' + Name + '"]')

    '''
    FKN:           removes an EntityType by Name
    Name:          Name of the node                                              REQUIRED
    Schema:        Parent-Element; may be different of current work schema       OPTIONAL
    '''
    def removeEntityType(self, Name, Schema = None):

        if Schema == None:
            Schema = self.schema

        ToRemove = Schema.find('.//EntityType[@Name="' + Name + '"]')
        if ToRemove:
            ToRemove.getparent().remove(ToRemove)

    def addKey(self, ParentNode, KeyName, *args):

        NewNode = xmlstruc.SubElement(ParentNode, "Key")
        xmlstruc.SubElement(NewNode, "PropertyRef", Name=KeyName)

        if self.getProperty(KeyName, ParentNode) == None:
            self.addProperty(ParentNode, KeyName, {"Type": "Edm.String"})

    '''
    FKN:           adds a new Node of namespace "Property" to RootElement with at least Name as specification
    ParentNode:    source-Element                                                REQUIRED
    propname:      defines the Name of the new element                           REQUIRED
    *args:         defines further specification of node                         OPTIONAL
    '''
    def addProperty(self, ParentNode, PropName, *args):

        NewNode = xmlstruc.SubElement(ParentNode, "Property", Name=PropName)

        if args:
            try:
                for item in args:
                    for key, value in item.iteritems():
                        NewNode.set(key, value)
            except:
# TODO: define exception
                print "no dict"

    '''
    FKN:           returns a Property by Name
    Name:          Name of the node                                              REQUIRED
    Schema:        Parent-Element; may be different of current work schema       OPTIONAL
    '''
    def getProperty(self, Name, Schema=None):

        if Schema == None:
            Schema = self.schema
        return Schema.find('.//Property[@Name="' + Name + '"]')

    '''
    FKN:           adds a new Node of namespace "NavigationProperty" to RootElement with at least Name as specification
    ParentNode:    defines the parent of the new element                         REQUIRED
    propname:      defines the Name of the new element                           REQUIRED
    *args:         defines further specification of node                         OPTIONAL
    '''
    def addNavigationProperty(self, ParentNode, NavName, *args):

        NewNode = xmlstruc.SubElement(ParentNode, "NavigationProperty", Name=NavName)

        if args:
            try:
                for item in args:
                    for key, value in item.iteritems():
                        NewNode.set(key, value)
            except:
# TODO: define exception
                print "no dict"

    '''
    FKN:           returns a NavigationProperty by Name
    Name:          Name of the node                                              REQUIRED
    Schema:        Parent-Element; may be different of current work schema       OPTIONAL
    '''
    def getNavigationProperty(self, Name, Schema=None):

        if Schema == None:
            Schema = self.schema
        return Schema.find('.//NavigationProperty[@Name="' + Name + '"]')

    '''
    FKN:           returns a NavigationProperty by Name
    Name:          Name of the node                                              REQUIRED
    Schema:        Parent-Element; may be different of current work schema       OPTIONAL
    '''
    def changeNavigationPropertyAttrib(self, NavName, AttribName, NewValue, Schema=False):

        if Schema == False:
            Schema = self.schema

        self.getNavigationProperty(NavName, Schema).attrib[AttribName] = NewValue

    '''
    FKN:           adds a new Node "EntityContainer" to self.schema with at least Name as specification
    Name:          Name of the node                                              REQUIRED
    Schema:        Parent-Element; may be different of current work schema       OPTIONAL
    *args:         defines further specification of node                         OPTIONAL
    '''
    def addEntityContainer(self, ECName, EntityType, Association, Schema=None, *args):

        if Schema == None:
            Schema = self.schema

        # identify last character to replace "y" with "ie"
        EntitySetName = replaceSingle(EntityType)
        AssociationName = replaceSingle(Association)

        NewNode = xmlstruc.SubElement(Schema, "EntityContainer", Name=ECName)
        # umbedingt muss der bool-wert mit allen Buchstaben KLEIN geschrieben sein!!! -> pyslet kann sonst den wert nicht parsen 
        #NewNode.set(xmlstruc.QName(META_NS, "IsDefaultEntityContainer"), "false")

        EntitySet = xmlstruc.SubElement(NewNode, "EntitySet", Name=EntitySetName)
        AssociationSet = xmlstruc.SubElement(NewNode, "AssociationSet", Name=AssociationName)

        Parent = xmlstruc.SubElement(AssociationSet, "End", Role="Parent")
        Parent.set("EntitySet", EntitySetName)
        Child = xmlstruc.SubElement(AssociationSet, "End", Role="Child")
        Child.set("EntitySet", EntitySetName)

        if args:
            try:
                for item in args:
                    for key, value in item.iteritems():
                        NewNode.set(key, value)
            except:
# TODO: define exception
                print "no dict"


    '''
    FKN:           generates an EntityContainer out of the given schema
#TODO: right now generates one container, but more entity and associations sets!!!
    ECName:        Name of the node                                              REQUIRED
    Schema:        The name of the conceptual model entity container. This       OPTIONAL
                   name is used as the class name of the generated context
                   class
    '''
    def autoEntityContainer(self, ECName, Schema=False):

        if Schema == False:
            Schema = self.schema

        findflag = False

        # basic work -> generate an EntityContainer
        NewNode = xmlstruc.SubElement(Schema, "EntityContainer", Name=ECName)
        NewNode.set(xmlstruc.QName(META_NS, "IsDefaultEntityContainer"), "true")

        # search the addressed EntityType
        for entitytype in Schema.findall("EntityType"):
            NewNode2 = xmlstruc.SubElement(NewNode, "EntitySet", Name=entitytype.attrib['Name']+"_Set")
            NewNode2.set("EntityType", Schema.attrib['Namespace']+"."+entitytype.attrib['Name'])
            if len(entitytype.findall("NavigationProperty")) > 0:
                for existAss in Schema.findall("Association"):
                    AssName = ""
                    ESName_Child = ""
                    for i, child in enumerate(existAss.getchildren()):
                        if (re.split(Schema.attrib['Namespace']+".", child.get("Type"))[1]+"s" == entitytype.attrib['Name']+"s") and (i == 0):
                            AssName = re.split(Schema.attrib['Namespace']+".", child.get("Type"))[1]+ "_Set"
                            findflag = True
                        if findflag and (i == 1):
                            ESName_Child = re.split(Schema.attrib['Namespace']+".", child.get("Type"))[1]+ "_Set"
                            findflag = False
                    if AssName != "":
                        if re.match("SubSets", existAss.attrib['Name']):
                            RoleA = "Parent"
                            RoleB = "Child"
                        elif re.match("Parents", existAss.attrib['Name']):
                            RoleA = "Child"
                            RoleB = "Parent"
                        else:
                            RoleA = "Entity_A"
                            RoleB = "Entity_B"
                        AssociationSet = xmlstruc.SubElement(NewNode, "AssociationSet", Name=existAss.attrib['Name']+"Set")
                        AssociationSet.set("Association", Schema.attrib['Namespace']+"."+existAss.attrib['Name'])
                        Parent = xmlstruc.SubElement(AssociationSet, "End", Role=RoleA)
                        Parent.set("EntitySet", AssName)
                        Child = xmlstruc.SubElement(AssociationSet, "End", Role=RoleB)
                        Child.set("EntitySet", ESName_Child)

    def sortEntries(self, Schema=False):

        if Schema == False:
            Schema = self.schema

        data = []

        for item in Schema.iterchildren():
            if item.tag == "EntityContainer":
                item.getparent().remove(item)
                Schema.insert(0, item)
                for subitem in item.iterchildren():
                    data.append(xmlstruc.tostring(subitem))
                    subitem.getparent().remove(subitem)

        data.sort(reverse=True)
        
        for item in Schema.iterchildren():
            if item.tag == "EntityContainer":
                for entry in data:
                    item.append(xmlstruc.fromstring(entry))


        #return NewObject

# TODO: change order of schema
        # order = [Schema[len(Schema)-1],Schema[:len(Schema)-2]]
        # print len(Schema)
        # print xmlstruc.tostring(order, pretty_print=True)

    '''
    FKN:           returns attr "FromRole"
    RETURN:        Parent-Element; may be different of current work schema
    '''
    def getFromRole(self, Node):

# TODO: Check WHATEVER node it must be
        return Node.attrib['FromRole']

    '''
    FKN:           returns a NavigationProperty by Name
    Name:          Name of the node                                              REQUIRED
    Schema:        Parent-Element; may be different of current work schema       OPTIONAL
    '''
    def getRelatedAssociation(self, AssName, Schema=None):

        if Schema == None:
            Schema = self.schema

        for item in Schema.findall("Association"):
            for subitem in item.findall('End'):
                if re.search("." + AssName, subitem.attrib['Type']):
                    return replaceSingle(item.attrib['Name'])

    def getEntityContainer(self, Name, Schema=None):

        if Schema == None:
            Schema = self.schema


    def getEntitySet(self, Name, Schema=None, *attr):

        if Schema == None:
            Schema = self.schema
        return Schema.find('.//EntitySet[@Name="' + Name + '"]')

    '''
    FKN:           adds a new Node of namespace "Association" to Schema with at least Name as specification
    Schema:        source
    AssName:       defines the Name of the Association                           REQUIRED
    Schema:        Parent-Element; may be different of current work schema       OPTIONAL
    *args:         defines further specification of node                         OPTIONAL
    '''
    def addAssociation(self, AssName, ParentAssignedEntity, ChildAssignedEntity, Schema = None, FromRole = "Parent", FromNum = False, ToRole = "Child", ToNum = True, *args):

        if Schema == None:
            Schema = self.schema

        NewNode = xmlstruc.SubElement(Schema, "Association", Name=AssName)
# TODO: Check if their are other associations, e.g. EQAUL
        Parent = xmlstruc.SubElement(NewNode, "End", Role = FromRole, Type = Schema.attrib['Namespace'] + "." + ParentAssignedEntity)
        # needed to get a nice order of specifications
        if FromNum:
            Parent.set("Multiplicity", "*")
        else:
            Parent.set("Multiplicity", "0..1")
        Child = xmlstruc.SubElement(NewNode, "End", Role = ToRole, Type = Schema.attrib['Namespace'] + "." + ChildAssignedEntity)
        if ToNum:
            Child.set("Multiplicity", "*")
        else:
            Child.set("Multiplicity", "0..1")

        if args:
            try:
                for item in args:
                    for key, value in item.iteritems():
                        NewNode.set(key, value)
            except:
# TODO: define exception
                print "no dict"

    '''
    FKN:           returns a Association by Name
    Name:          Name of the node                                              REQUIRED
    Schema:        Parent-Element; may be different of current work schema       OPTIONAL
    '''
    def getAssociation(self, Name, Schema=None):

        if Schema == None:
            Schema = self.schema
        return Schema.find('.//Association[@Name="' + Name + '"]')

    '''
    FKN:           prints the whole structure contained by self.root into a given file. XML-Header is attached before
    filename:      Name of the Output-File                                       REQUIRED
    '''
    def writeToFile(self, filename):

        self.doc = xmlstruc.ElementTree(self.root)
        self.doc.write(open(filename + ".xml", "w"), pretty_print=True, xml_declaration=True, encoding=VENCODING, standalone=True)

'''
FKN:           returns a string with prefix "ies" if the original strings end with "y" otherwise returns string + "s"
string:        string                                                        REQUIRED
RETURN:        string
'''
def replaceSingle(string):

    # identify last character to replace "y" with "ie"
    if string[-1:] == "s":
        Newstring  =string
    elif string[-1:] == "y":
        k = string.rfind("y")
        Newstring = string[:k] + "ie" + "s"
    else:
        Newstring = string + "s"

    return Newstring
