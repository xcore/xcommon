#include <iostream>
#include "tinyxml.h"
#include <string>
#include <set>

int main(int argc, char *argv[]) {

  if (argc < 3)
    exit(1);

  TiXmlDocument project(argv[1]);

  bool loadOkay = project.LoadFile();

  if (!loadOkay) {
    std::cerr << "Cannot load XML file `" << argv[0] << "'" << std::endl;
    std::cerr << project.ErrorDesc() << std::endl;
    exit(1);
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


  project.Print(stdout);

  return 0;
}
