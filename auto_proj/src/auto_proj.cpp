#include <iostream>
#include "tinyxml.h"
#include <string>
#include <set>

#define DEBUG 1

void ASSERT_XML_EXISTS(std::string message, void *p) {

  if (!p) {
#if DEBUG
    std::cerr << "ERROR:: missing XML" << std::endl;
    std::cerr << message << std::endl;
#endif
    exit(0);
  }
}

void check_and_advise(int line, bool test) {
  if (!test) {
#if DEBUG
    std::cerr << "project xml fail: line " << line << std::endl;
#endif
    exit(0);
  }
}

#define CHECK_AND_ADVISE(T) check_and_advise(__LINE__, T)

int main(int argc, char *argv[]) {

  TiXmlDocument project(argv[1]);
  bool loadOkay = project.LoadFile();

  if (!loadOkay) {
    std::cerr << "Cannot load XML file `" << argv[0] << "'" << std::endl;
    std::cerr << project.ErrorDesc() << std::endl;
    exit(1);
  }


  TiXmlNode *cproject_xml = project.FirstChild("cproject");

  CHECK_AND_ADVISE(cproject_xml != NULL);

  TiXmlNode *storage_module_xml =
      cproject_xml->FirstChildElement("storageModule");

  CHECK_AND_ADVISE(storage_module_xml != NULL);

  TiXmlNode *cconfiguration_xml =
    storage_module_xml->FirstChildElement("cconfiguration");

  CHECK_AND_ADVISE(cconfiguration_xml != NULL);

  const char *cconfiguration_id =
    cconfiguration_xml->ToElement()->Attribute("id");

  CHECK_AND_ADVISE(cconfiguration_id != NULL);

  std::cerr << cconfiguration_id << std::endl;
  std::cerr << "cproject\n";

  exit(0);


  if (!project.FirstChild("projectDescription")) {
    project.Print(stdout);
    exit(0);
  }

  TiXmlNode *projects_xml =
    project.FirstChild("projectDescription")->ToElement()->FirstChild("projects");


  std::set<std::string> current_projects;


  if (projects_xml) {
    TiXmlNode *project_xml =
      projects_xml->FirstChildElement("project");

    while (project_xml) {
      std::string proj(project_xml->ToElement()->GetText());
      TiXmlNode *next_project_xml = project_xml->NextSibling("project");
      current_projects.insert(proj);
      projects_xml->RemoveChild(project_xml);
      project_xml = next_project_xml;
    }


    for (int i=2;i<argc;i++) {
      std::string new_proj(argv[i]);
      current_projects.insert(new_proj);

    }

  for(std::set<std::string>::iterator proj = current_projects.begin();
      proj != current_projects.end();
      proj++)
    {
      TiXmlElement* new_element = new TiXmlElement("project");
      TiXmlText* txt = new TiXmlText((*proj).c_str());
      new_element->LinkEndChild(txt);
      projects_xml->InsertEndChild(*new_element);
    }

  }


  project.Print(stdout);

  return 0;
}
