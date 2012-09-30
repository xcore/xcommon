#include <string>
#include <iostream>
#include <fstream>
using namespace std;


void strReplace(std::string& str, 
                const std::string& from, 
                const std::string& to)
{
  size_t pos = 0;
  while((pos = str.find(from, pos)) != std::string::npos)
  {
     str.replace(pos, from.length(), to);
     pos += to.length();
  }
}

void strReplaceUpto(std::string& str, 
                    const std::string& delim, 
                    const std::string& to)
{
  size_t pos = 0;
  if ((pos = str.find(delim, pos)) != std::string::npos)
  {
     str.replace(0, pos, to);
  }
}

void fixSpaces(std::string & str)
{
  size_t pos = 0;
  while ((pos = str.find('/', pos)) != std::string::npos)
    {
      //      std::cerr << pos <<
      pos++;
      while ((pos < str.length()) && (str[pos] != '.'))
        {
          if (str[pos] == ' ' && str[pos-1] != '\\') {
            str.insert(pos,"\\");
            pos++;
          }
          pos++;
        }
    }
}

void process(std::string& str, 
             int argc,
             char **argv,
             bool first_line)
{
  if (argc < 3)
    return;

  // Perform search and replaces
  for(int i=3;i+1 < argc;i+=2)
    {     
      strReplace(str, argv[i], argv[i+1]);
    }

  // Add extra target to dependency
  if (first_line)
    strReplaceUpto(str,":",argv[2]);


  // Fix up spaces in paths
  fixSpaces(str);
}

int main(int argc,char **argv) 
{
  ifstream file;
  string line;
  bool first_line = true;
  file.open(argv[1]);

  if (file.is_open()) {    
    while (file.good()) {
      getline(file, line);
      process(line, argc, argv, first_line);
      cout << line << endl;
      first_line = false;
    }
    file.close();
  }
  return 0;
}
