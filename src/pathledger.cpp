#include <algorithm>
#include <cctype>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <tuple>
namespace fs=std::filesystem;
std::string json(const std::string&s){std::string r="\"";const char*h="0123456789abcdef";for(unsigned char c:s){if(c=='"'||c=='\\'){r+='\\';r+=c;}else if(c<32){r+="\\u00";r+=h[c>>4];r+=h[c&15];}else r+=c;}return r+'"';}
std::string lower(std::string s){for(auto&c:s)if(c>='A'&&c<='Z')c+=32;return s;}
size_t units(const std::string&s){size_t n=0;for(unsigned char c:s){if((c&0xc0)!=0x80)n+=(c>=0xf0?2:1);}return n;}
struct Issue{std::string severity,code,path,detail;};
int program_main(int argc,char**argv){
 if(argc!=2){std::cerr<<"Usage: pathledger DIRECTORY\n";return 2;}
 std::error_code ec;fs::path root=fs::weakly_canonical(fs::u8path(argv[1]),ec);
 if(ec||!fs::is_directory(root,ec)){std::cerr<<"Input must be an accessible directory.\n";return 2;}
 std::vector<Issue> issues;std::vector<std::pair<fs::path,size_t>> stack{{root,0}};size_t entries=0,files=0,dirs=0,symlinks=0;uintmax_t bytes=0;bool truncated=false;
 auto add=[&](std::string sev,std::string code,std::string path,std::string detail){if(issues.size()<20000)issues.push_back({sev,code,path,detail});else truncated=true;};
 while(!stack.empty()&&entries<100000){auto [current,depth]=stack.back();stack.pop_back();fs::directory_iterator it(current,fs::directory_options::none,ec),end;
 if(ec){add("error","UNREADABLE_DIRECTORY",current.lexically_relative(root).generic_u8string(),ec.message());ec.clear();continue;}
 std::map<std::string,std::string> names;
 for(;it!=end&&entries<100000;it.increment(ec)){
 if(ec){add("error","ENUMERATION_ERROR",current.lexically_relative(root).generic_u8string(),ec.message());ec.clear();break;}
 ++entries;auto p=it->path();std::string name=p.filename().u8string(),rel=p.lexically_relative(root).generic_u8string();
 std::string comparable=lower(name);while(!comparable.empty()&&(comparable.back()=='.'||comparable.back()==' '))comparable.pop_back();
 auto old=names.find(comparable);if(old!=names.end())add("error","CASE_OR_TRIM_COLLISION",rel,"Conflicts with sibling "+old->second+" under common Windows case/trim rules.");else names[comparable]=name;
 bool invalid=false,nonascii=false;for(unsigned char c:name){if(c<32||std::string("<>:\"|?*\\").find(c)!=std::string::npos)invalid=true;if(c>=128)nonascii=true;}
 if(invalid)add("error","INVALID_WINDOWS_CHARACTER",rel,"Contains a character unavailable in ordinary Windows file names.");
 if(!name.empty()&&(name.back()=='.'||name.back()==' '))add("error","TRAILING_DOT_OR_SPACE",rel,"Ordinary Win32 APIs may remove the trailing dot or space.");
 auto base=lower(name.substr(0,name.find('.')));while(!base.empty()&&base.back()==' ')base.pop_back();
 bool reserved=base=="con"||base=="prn"||base=="aux"||base=="nul"||(base.size()==4&&(base.substr(0,3)=="com"||base.substr(0,3)=="lpt")&&base[3]>='1'&&base[3]<='9');
 reserved=reserved||base=="com¹"||base=="com²"||base=="com³"||base=="lpt¹"||base=="lpt²"||base=="lpt³";
 if(reserved)add("error","RESERVED_DEVICE_NAME",rel,"Rename this Windows device name before archive migration.");
 if(units(name)>255)add("error","LONG_COMPONENT",rel,"A path component exceeds 255 UTF-16 code units.");
 if(units(rel)+11>=260)add("warning","LEGACY_MAX_PATH",rel,"Projected C:\\Archive\\ path reaches the legacy 260-unit boundary; test long-path support or shorten it.");
 if(nonascii)add("review","UNICODE_REVIEW",rel,"Unicode name retained intact. Verify UTF-16 APIs and application encoding; this is not a defect by itself.");
 auto status=it->symlink_status(ec);if(ec){add("error","STATUS_ERROR",rel,ec.message());ec.clear();continue;}
 if(fs::is_symlink(status)){++symlinks;add("review","SYMLINK_SKIPPED",rel,"Link recorded but not followed; external targets are never traversed.");continue;}
 if(fs::is_directory(status)){++dirs;if(depth<63)stack.push_back({p,depth+1});else{truncated=true;add("warning","DEPTH_LIMIT",rel,"Depth limit 64 reached; deeper entries were not inspected.");}}
 else if(fs::is_regular_file(status)){++files;auto size=it->file_size(ec);if(!ec)bytes+=size;else{add("error","SIZE_ERROR",rel,ec.message());ec.clear();}}
 }
 }
 if(entries>=100000||!stack.empty())truncated=true;
 std::sort(issues.begin(),issues.end(),[](const Issue&a,const Issue&b){return std::tie(a.path,a.code)<std::tie(b.path,b.code);});
 size_t errors=0,warnings=0,reviews=0;for(auto&i:issues){errors+=i.severity=="error";warnings+=i.severity=="warning";reviews+=i.severity=="review";}
 std::cout<<"{\"root\":"<<json(root.u8string())<<",\"entries\":"<<entries<<",\"files\":"<<files<<",\"directories\":"<<dirs<<",\"bytes\":"<<bytes<<",\"symlinks\":"<<symlinks<<",\"errors\":"<<errors<<",\"warnings\":"<<warnings<<",\"reviews\":"<<reviews<<",\"truncated\":"<<(truncated?"true":"false")<<",\"projection\":\"C:\\\\Archive\\\\\",\"issues\":[";
 bool first=true;for(auto&i:issues){if(!first)std::cout<<',';first=false;std::cout<<"{\"severity\":"<<json(i.severity)<<",\"code\":"<<json(i.code)<<",\"path\":"<<json(i.path)<<",\"detail\":"<<json(i.detail)<<'}';}std::cout<<"]}\n";
 return 0;
}

#ifdef _WIN32
int wmain(int argc,wchar_t**wargv){
 std::vector<std::string> args; for(int i=0;i<argc;++i) args.push_back(fs::path(wargv[i]).u8string());
 std::vector<char*> ptrs; for(auto&arg:args) ptrs.push_back(arg.data());
 return program_main(argc,ptrs.data());
}
#else
int main(int argc,char**argv){return program_main(argc,argv);}
#endif
