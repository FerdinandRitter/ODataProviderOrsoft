'''
Created on 03.05.2015

@author: Ferdinand Ritter
'''

'''
basic libs
'''
import re
import os.path
import types

from lxml import etree
import threading, logging
from wsgiref.simple_server import make_server
'''
needed pyslet parts
'''
import pyslet.odata2.metadata as edmx
import pyslet.odata2.core as odata
from pyslet.odata2.server import ReadOnlyServer

'''
own files
'''
import odata_demomodel
from ODataEdmx import edmxWriter




class ODataStructureModel(object):
    '''
    1.this class gets all information out of the data-model, that are required to build a edmx data-structure-model -> generates the edmx

    2.runs an odata-application on given server
    '''

    def __init__(self, *params):
        '''
        basic object attr are assigned
        '''
        self.NAV_PROP_NAME_DIR = "SubSets"
        self.NAV_PROP_NAME_DIR_RETURN = "Parents"
        self.NAV_RELATIONSHIP_DIR = "Directory"
        self.NAV_FROM_ROLL_DIR = "Parent"
        self.NAV_TO_ROLL_DIR = "Child"

        self.NAV_PROP_NAME_LEV = "References"
        self.NAV_PROP_NAME_LEV_RETURN = "ToReference"
        self.NAV_RELATIONSHIP_LEV = "Level"
        self.NAV_FROM_ROLL_LEV = "Entity_A"
        self.NAV_TO_ROLL_LEV = "Entity_B"

        self.edmx_file_name = "ODATA_Modell"
        self.edmx_schema_name = "SNameSchema"
        self.edmx_container_name ="SNContainer"

        # name the service in the brackets -> default value is "DataServices"
        self.edmx = edmxWriter()
        self.edmx_schema = self.edmx.addSchema(self.edmx_schema_name)

        # object_keys werden spaeter die nodes im edmx (parent=schema)
        self.object_keys = []
        self.object_properties_fields = dict()
        self.object_properties_workers = dict()

        self.object_properties_references = dict()
        self.references_counter = 0
        self.assications_pair_LEV = dict()
        self.subsets_counter = 0

        self.object_properties_subsets = dict()
        self.assications_pair_DIR = dict()

        self.testprop = []
        
        self.objct_metamodell = odata_demomodel.getBOs()

    
    def getObjectKeys(self):
        '''
        FKN:            main funciton of ths class -> collecting all the entries of the database
        RETURN:
        '''

        for object_name in self.objct_metamodell:
            if not object_name in self.object_keys:
                self.object_keys.append(object_name)
            # provide empty property dicts
            self.object_properties_fields = dict()
            self.object_properties_workers = dict()
            self.object_properties_references = dict()
            self.object_properties_subsets = dict()
            for key in odata_demomodel.getBOInfos(object_name).iterkeys():
                if key == "fields" and not self.object_properties_fields:
                    self.object_properties_fields = self.getObjectPropertiesFields(object_name)
                if key == "worker" and not self.object_properties_workers:
                    self.object_properties_workers = self.getObjectPropertiesWorkers(object_name)
                if key == "subsets" and not self.object_properties_subsets:
                    self.object_properties_subsets = self.getObjectPropertiesSubsets(object_name)
                if key == "references" and not self.object_properties_references:
                    self.object_properties_references = self.getObjectPropertiesReferences(object_name)
            self.createEdmxEntry(object_name)

        self.edmx.autoEntityContainer(self.edmx_container_name, self.edmx_schema)
        
        self.edmx.sortEntries(self.edmx_schema)

        self.edmx.writeToFile(self.edmx_file_name)


    def getObjectPropertiesFields(self, objectKey):
        '''
        FKN:            returns a dict of property name (as key) and data-type (as value)
        objectKey:      name of requested object                         REQUIRED
        RETURN:         Dictonary
        '''

        fields = dict()

        for item in odata_demomodel.getBOFields(objectKey):
            values = list(item)
            try:#if not values[0] in self.object_properties:
                fields[values[0]] = re.sub(" ", "", re.sub("\'*\>*", "", re.split("type", values[1])[1]))
            except:
                fields[values[0]] = values[1]

        return fields


    def getObjectPropertiesWorkers(self, objectKey):
        '''
        FKN:            returns a dict of property name (as key) and data-type (as value)
        objectKey:      name of requested object                         REQUIRED
        RETURN:         Dictonary
        '''

        workers = dict()

        #for item in list(odata_demomodel.getBOWorkers(objectKey)):
        #    workers[item] = ""

        return workers


    def getObjectPropertiesSubsets(self, objectKey):
        '''
        FKN:            returns a dict of navigation_property name (as key) and data-type (as value)
        objectKey:      name of requested object                         REQUIRED
        RETURN:         Dictonary
        '''

        subsets = dict()

        for item in odata_demomodel.getBOSubobjects(objectKey):
            values = list(item)
            print values
            #if not values[0] in self.object_properties:
            try:
                if (re.sub(" ", "", re.sub("\'*\>*", "", re.split("type", values[1])[1])) in self.objct_metamodell):
                    subsets[values[0]] = re.sub(" ", "", re.sub("\'*\>*", "", re.split("type", values[1])[1]))
            except:
                if (values[1] in self.objct_metamodell):
                    subsets[values[0]] = values[1]

        return subsets


    def getObjectPropertiesReferences(self, objectKey):
        '''
        FKN:            returns a dict of navigation_property name (as key) and data-type (as value)
        objectKey:      name of requested object                         REQUIRED
        RETURN:         Dictonary
        '''

        references = dict()

        #print odata_demomodel.getBOReferences(objectKey)
        for item in odata_demomodel.getBOReferences(objectKey):
            values = list(item)
            #if not values[0] in self.object_properties:
            try:
                if (re.sub(" ", "", re.sub("\'*\>*", "", re.split("type", values[1])[1])) in self.objct_metamodell):
                    references[values[0]] = re.sub(" ", "", re.sub("\'*\>*", "", re.split("type", values[1])[1]))
            except:
                if (values[1] in self.objct_metamodell):
                    references[values[0]] = values[1]

        return references


    def assignParentChild(self, parentname, childname):
        '''
        FKN:            return, if childname match, a dict-entry
        parentname:     key of dict-entry                                REQUIRED
        childname:      value of dict-entry                              REQUIRED
        RETURN          None/Dictonary
        '''

        for object_name in odata_demomodel.getBOs():
            if object_name == childname:
                return {parentname: childname}

        return None


    def assignEquatedPair(self, parentname, childname):
        '''
        FKN:            return, if childname match, a dict-entry
        parentname:     key of dict-entry                                REQUIRED
        childname:      value of dict-entry                              REQUIRED
        RETURN          None/Dictonary
        '''

        for object_name in odata_demomodel.getBOs():
            if object_name == childname:
                return {parentname: childname}

        return None


    def createEdmxEntry(self, EntityName):
        '''
        FKN:
        EntityName:                                                      REQUIRED
        RETURN:
        '''

        # create a new entitytype in the main schema
        self.edmx.addEntityType(EntityName, self.edmx_schema)

        # defining the access key on the entitytype
        self.edmx.addKey(self.edmx.getEntityType(EntityName),"ID")

        # define properties and navigation properties
        for key, value in self.object_properties_fields.iteritems():
            self.edmx.addProperty(self.edmx.getEntityType(EntityName), key, {"Type": "Edm.String"})# Eig muesste hier fuer den Type der wert von "value" gesetzt werden

        for key, value in self.object_properties_workers.iteritems():
            self.edmx.addProperty(self.edmx.getEntityType(EntityName), key, {"Type": "Edm.String"})

        # there is a distinction between Parent-Child and Both-on-the-same-level connection
        if len(self.object_properties_subsets) != 0:
            # index is used to get an unique connection name
            i = 0
            for key, value in self.object_properties_subsets.iteritems():
                self.edmx.addNavigationProperty(self.edmx.getEntityType(EntityName), self.NAV_RELATIONSHIP_DIR+str(i), {"Relationship": self.edmx_schema.attrib['Namespace'] + "." + self.NAV_PROP_NAME_DIR+str(self.subsets_counter),"FromRole": self.NAV_FROM_ROLL_DIR, "ToRole": self.NAV_TO_ROLL_DIR})
                self.edmx.addAssociation(self.NAV_PROP_NAME_DIR+str(self.subsets_counter), EntityName, value, self.edmx_schema, self.NAV_FROM_ROLL_DIR, False, self.NAV_TO_ROLL_DIR, True)
                self.subsets_counter = self.subsets_counter + 1
                i = i + 1

        if len(self.object_properties_references) != 0:
            # index is used to get an unique connection name
            i = 0
            for key, value in self.object_properties_references.iteritems():
                self.edmx.addNavigationProperty(self.edmx.getEntityType(EntityName), self.NAV_RELATIONSHIP_LEV+str(i), {"Relationship": self.edmx_schema.attrib['Namespace'] + "." + self.NAV_PROP_NAME_LEV+str(self.references_counter),"FromRole": self.NAV_FROM_ROLL_LEV, "ToRole": self.NAV_TO_ROLL_LEV})
                self.edmx.addAssociation(self.NAV_PROP_NAME_LEV+str(self.references_counter ), EntityName, value, self.edmx_schema, self.NAV_FROM_ROLL_LEV, True, self.NAV_TO_ROLL_LEV, True)
                self.references_counter = self.references_counter + 1
                i = i + 1 

# TODO: koennte auch assignParentChild nutzen


class FSCollection(odata.EntityCollection):
    '''
    Uses EntityCollection of pyslet to generate entities for the server
    '''

    def itervalues(self):
        '''
        FKN:            initial function, if a data is requested by a URL call
        RETURN:         ?list?
        '''

        return self.order_entities(
            self.expand_entities(self.filter_entities(self.generate_entities())))


    def generate_entities(self):
        '''
        FKN:
        RETURN:
        '''

        self.ListOfConnectionTypes = [
                "setof_requiredfields", "setof_notifications", "setof_proceeds", 
                "setof_conditions", "setof_followsteps", "setof_fieldvalues", 
                "setof_usergrouprefs", "setof_properties", "setof_userProfileReferences",
                "setof_comments", "setof_steps", "setof_fieldinfos",
                "setof_keyvalues", "setof_formitems", "setof_userprofiles"]
        
        """List all the files in our file system /"""
        EntityTypeName = re.sub("_Set", "", self.entity_set.name)

        for EntryID in odata_demomodel.getBOAEntities(EntityTypeName):
            e = self.new_entity()
            e['ID'].set_from_value(EntryID)
            self._getProperties(e, EntityTypeName, EntryID)
            yield e


    def __getitem__(self, ID):
#TODO: find single entities
        '''
        FKN:
        ID:
        RETURN:
        '''

        self.ListOfConnectionTypes = [
                "setof_requiredfields", "setof_notifications", "setof_proceeds", 
                "setof_conditions", "setof_followsteps", "setof_fieldvalues", 
                "setof_usergrouprefs", "setof_properties", "setof_userProfileReferences",
                "setof_comments", "setof_steps", "setof_fieldinfos",
                "setof_keyvalues", "setof_formitems", "setof_userprofiles", "list_of_connection_types"]

        EntityTypeName = self.entity_set.entityType.name

        e = self.new_entity()
        self._getProperties(e, EntityTypeName, ID)
        print "hello" 
        #yield e
        #e = self.new_entity()
        # look into self[ID]
        #e['ID'].set_from_value(ID)
        #self._getProperties(e, EntityTypeName, EntryID)
        #yield e
        
        # ID -> try
        #try:
            
            # get content of Database through ID
            
            # CHECK WHAT IT DOES: if self.check_filter(e):
            # CHECK WHAT IT DOES:        if self.expand or self.select:

            # newentity bind to the collection
            
        #except ValueError:
            #raise KeyError("No such ID: %s" % ID)
        

        #return #odata.EntityCollection.__getitem__(self, ID)


    def _getProperties(self, e, EntityTypeName, ID):
        '''
        FKN:
        e:
        EntityTypeName:
        ID:
        RETURN:
        '''

        for property, value in odata_demomodel.getBOAProperties(EntityTypeName, ID).iteritems():
            if re.match("ref", property):
                continue
            elif property == "OBJECT_ID": 
                continue
            elif property in self.ListOfConnectionTypes:
                continue
            elif type(value) == types.ListType:
                if len(value) == 0:
                    e[property].set_from_value("Not defined")
                else:
                    e[property].set_from_value(value[0])
            else:
                if property == "":
                    e[property].set_from_value("Not defined")
                else:
                    # just ascii coded strings are accepted
                    try:
                        e[property].set_from_value(value)
                    except ValueError:
                        e[property].set_from_value("Not defined")

        e.exists = True



class SNReference(odata.EntityCollection):
    '''
    basically the same fucntionality as the SNCollection-Class, but specialisted on NavigationProperties/-entities
    '''

    def itervalues(self):
        '''
        FKN:            initial function, if a data is requested by a URL call
        RETURN:         ?list?
        '''

        return self.generate_entities()
    
    def generateEntity(self):
        '''
        FKN:
        RETURN:
        '''

        # get 'ID' of origin node -> navigation: EDMX 'fromRole'
        currentEntityID = self.from_entity['ID'].value
        # get 'EntityType'.'name' to get 'NavigationProperty's
        currentEntityTypeName = self.entityTypeName

        # generate objective
        try:
            for navprop, value in odata_demomodel.getBOAProperties(currentEntityTypeName, currentEntityID).iteritems():
                e = self.new_entity()
                if re.match("ref", navprop):
                    print property
                    print value
                    print "-----------------------------------------" 
                    e[navprop].set_from_value(value)
                e.exists = True
                yield e
        except:
            pass
        

    def __getitem__(self, key):
        '''
        diese methide wird jetzt benoetigt... sie ruft die verlinkte Instanz auf
        '''
        return odata.EntityCollection.__getitem__(self, key)



class SNSubset(odata.EntityCollection):
    '''
    basically the same fucntionality as the SNCollection-Class, but specialisted on NavigationProperties/-entities
    '''

    def itervalues(self):
        '''
        FKN:            initial function, if a data is requested by a URL call
        RETURN:         ?list?
        '''

        return self.generate_entities()
    
    def generateEntity(self):
        '''
        FKN:
        RETURN:
        '''

        # get 'ID' of origin node -> navigation: EDMX 'fromRole'
        currentEntityID = self.from_entity['ID'].value
        # get 'EntityType'.'name' to get 'NavigationProperty's
        currentEntityTypeName = self.entityTypeName

        try:
            for navprop, value in odata_demomodel.getBOAProperties(currentEntityTypeName, currentEntityID).iteritems():
                e = self.new_entity()
                if re.match("set", navprop):
                    print property
                    print value
                    print "-----------------------------------------" 
                    e[navprop].set_from_value(value)
                e.exists = True
                yield e
        except ValueError:
            # really unexpected, every path should have a parent
            # except for the root
            raise ValueError("Unexpected path error: %s" % parent_path)

    def __getitem__(self, key):
        '''
        diese methide wird jetzt benoetigt... sie ruft die verlinkte Instanz auf
        '''
        return odata.EntityCollection.__getitem__(self, key)



class ODataServer():
    '''
    proovides the functionality to (config and) run  a server
    '''

    def __init__(self, filename):
        '''
        FKN:            Some basic config
        RETURN:
        '''

        #: the port on which we'll listen for requests
        self.SERVICE_PORT = 8081

        #: the service root of our OData service
        self.SERVICE_ROOT = "http://localhost:%i/" % self.SERVICE_PORT

        # Name of a existing edmx_file
        self.edmxfilename = filename
        #
        self.pathtoedmx = os.path.join(os.path.split(__file__)[0], self.edmxfilename)


    def Meta_Model(self):
# sehr speziell die FKN -> muss auch/zumindest fuer anders geartete EDMX funktionieren 
        '''
        FKN:            Provides some required Data of the edmx-File 
        RETURN:
        '''

        doc = edmx.Document()

        with open(self.pathtoedmx, 'rb') as f:
            doc.Read(f)

        for EntityTypeName in odata_demomodel.getBOAs():
            container = doc.root.DataServices['SNameSchema.SNContainer.' + EntityTypeName + "_Set"]
            container.bind(FSCollection)
            #print etree.parse(path).getroot().iter()
            for item in etree.parse(self.pathtoedmx).getroot().iter("{http://schemas.microsoft.com/ado/2008/09/edm}EntityType"):
                if dict(item.attrib).values()[0] == EntityTypeName:
                    for NavProp in item.iter("{http://schemas.microsoft.com/ado/2008/09/edm}NavigationProperty"):
                        NavPropName = dict(NavProp.attrib).get("Name", None)
                        if re.match("Level", NavPropName):
                            container.BindNavigation(NavProp.tag, SNReference)
                        elif re.match("Directory", NavPropName):
                            container.BindNavigation(NavProp.tag, SNSubset)
                        else:
                            pass

        return doc


    def get_server_ready(self):
        '''
        FKN:            load all necessary functions of threading and server to have a runable server object 
        RETURN:
        '''

        doc = self.Meta_Model()

        server = ReadOnlyServer(serviceRoot=self.SERVICE_ROOT)
        server.SetModel(doc)
        self.app = server
        t = threading.Thread(target=self.run_server)
        t.setDaemon(True)
        t.start()
        logging.info("Starting OData server on %s" % self.SERVICE_ROOT)
        t.join()


    def run_server(self):
        '''
        FKN:            Starts the web server running
        RETURN:
        '''

        server = make_server('', self.SERVICE_PORT, self.app)
        logging.info("HTTP server on port %i running" % self.SERVICE_PORT)
        # Respond to requests until process is killed
        server.serve_forever()
