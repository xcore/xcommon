#include <iostream>
#include "tinyxml.h"
#include <string>
#include <set>
#include <vector>

TiXmlElement *getOrCreateChild(TiXmlElement *node,
                               std::string tag,
                               std::string attrPattern,
                               std::string attrValue,
                               bool &is_new_node)
{
  TiXmlElement *child = node->FirstChildElement(tag.c_str());
  is_new_node = false;
  while (child) {
    const char *attr0 = child->Attribute(attrPattern.c_str());
    if (attr0) {
      std::string attr = std::string(attr0);
      if (attr.find(attrValue) == 0) {
        break;
      }
    }
    child = child->NextSiblingElement(tag.c_str());
  }
  if (!child) {
    child = new TiXmlElement(tag.c_str());
    is_new_node = true;
  }
  return child;
}


void add_option_node(TiXmlElement *node, std::string option_id,
                   std::set<std::string> &orig_includes)
{
  bool is_new_node;
  TiXmlElement *option = getOrCreateChild(node,
                                          "option",
                                          "id",
                                          option_id,
                                          is_new_node);

  std::set<std::string> includes = orig_includes;



  TiXmlElement *listOptionValue = option->FirstChildElement("listOptionValue");

  while (listOptionValue) {
    const char *val0 = listOptionValue->Attribute("value");
    if (val0) {
      std::string val(val0);
      includes.erase(val);
    }
    listOptionValue = listOptionValue->NextSiblingElement("listOptionValue");
  }


  std::set<std::string>::iterator i;
  for(i=includes.begin(); i!=includes.end(); i++) {
    listOptionValue = new TiXmlElement("listOptionValue");
    listOptionValue->SetAttribute("builtIn","false");
    listOptionValue->SetAttribute("value",(*i).c_str());
    option->InsertEndChild(*listOptionValue);
  }

  if (is_new_node) {
    std::string option_id_num = option_id;
    option_id_num.append(".11111");
    option->SetAttribute("id",option_id_num.c_str());
    option->SetAttribute("valueType","includePath");
    option->SetAttribute("superClass",option_id.c_str());
    node->InsertEndChild(*option);
  }
}

void add_tool_node(TiXmlElement *node, std::string tool_id,
                   std::set<std::string> &includes) {
  bool is_new_node;
  TiXmlElement *tool = getOrCreateChild(node,
                                        "tool",
                                        "id",
                                        tool_id,
                                        is_new_node);

  add_option_node(tool, "gnu.c.compiler.option.include.paths", includes);
  add_option_node(tool, "com.xmos.c.compiler.option.include.paths", includes);

  if (is_new_node) {
    std::string tool_id_num = tool_id;
    tool_id_num.append(".11111");
    tool->SetAttribute("id",tool_id_num.c_str());
    tool->SetAttribute("name",tool_id.c_str());
    tool->SetAttribute("superClass",tool_id.c_str());
    node->InsertEndChild(*tool);
  }

}

void process(TiXmlElement *node, std::string path[], int i, int n,
             std::set<std::string> &includes,
             std::set<std::string> &old_includes)
{
  if (i == n) {
    const char *id0 = node->Attribute("id");
    if (id0) {
      std::string id = std::string(id0);
      if (id.find("com.xmos.cdt.toolchain")==0) {
        add_tool_node(node, "com.xmos.cdt.xc.compiler", includes);
        add_tool_node(node, "com.xmos.cdt.xc.compiler.base", old_includes);
        add_tool_node(node, "com.xmos.cdt.c.compiler.base", old_includes);
        add_tool_node(node, "com.xmos.cdt.cpp.compiler.base", old_includes);
        add_tool_node(node, "com.xmos.cdt.core.assembler.base", old_includes);
      }
    }
  }
  else {
    TiXmlElement *child = node->FirstChildElement(path[i].c_str());
    while (child) {
      process(child, path, i+1, n, includes, old_includes);
      child = child->NextSiblingElement(path[i].c_str());
    }
  }
  return;
}

int main(int argc, char *argv[]) {

  TiXmlDocument project(argv[1]);
  bool loadOkay = project.LoadFile();

  if (!loadOkay) {
    std::cerr << "Cannot load XML file `" << argv[0] << "'" << std::endl;
    std::cerr << project.ErrorDesc() << std::endl;
    exit(1);
  }

  std::string path[] = {"storageModule",
                        "cconfiguration",
                        "storageModule",
                        "configuration",
                        "folderInfo",
                        "toolChain"};

  TiXmlElement *cproject = project.FirstChildElement("cproject");

  if (cproject) {
    std::set<std::string> includes;
    std::set<std::string> old_includes;
    includes.insert("\"${XMOS_TOOL_PATH}/target/include\"");
    includes.insert("\"${XMOS_TOOL_PATH}/target/include/c++/4.2.1/xcore-xmos-elf\"");
    includes.insert("\"${XMOS_TOOL_PATH}/target/include/c++/4.2.1\"");
    includes.insert("\"${XMOS_TOOL_PATH}/target/include/gcc\"");

    old_includes.insert("\"${XMOS_DOC_PATH}/../target/include\"");
    old_includes.insert("\"${XMOS_DOC_PATH}/../target/include/c++/4.2.1/xcore-xmos-elf\"");
    old_includes.insert("\"${XMOS_DOC_PATH}/../target/include/c++/4.2.1\"");
    old_includes.insert("\"${XMOS_DOC_PATH}/../target/include/gcc\"");


    for (int i=2;i<argc;i++) {
      std::string include(argv[i]);
      include.insert(0,"\"${workspace_loc:/");
      include.append("}\"");
      includes.insert(include);
      old_includes.insert(include);
    }
    process(cproject, path, 0, 6, includes, old_includes);
  }
   project.Print(stdout);
  return 0;
}
