#!/usr/bin/env python
# coding:utf-8
#   |                                                          |
# --+----------------------------------------------------------+--
#   |   Code by : yasserbdj96                                  |
#   |   Email   : yasser.bdj96@gmail.com                       |
#   |   Github  : https://github.com/yasserbdj96               |
#   |   BTC     : bc1q2dks8w8uurca5xmfwv4jwl7upehyjjakr3xga9   |
# --+----------------------------------------------------------+--  
#   |        all posts #yasserbdj96 ,all views my own.         |
# --+----------------------------------------------------------+--
#   |                                                          |

#START{
#
def scandir(dirx="./"):
    x="""
$fileList=array();
$path='"""+dirx+"""';
if($handle=opendir($path)){
    while(false!==($entry=readdir($handle))){
        if($entry!="." && $entry!=".."){
            if(is_dir($entry)){
                $entry=$path.$entry."/";
            }else{
                $entry=$path.$entry;
            }
            $fileList[]=$entry;
        }
    }
    closedir($handle);
}
echo json_encode($fileList);"""
    return x
#
def scandir_all(dirx="./"):
    x="""
function getDirContents($dir="./",$relativePath=false){
    $fileList=array();
    $iterator=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir));
    foreach($iterator as $file){
        if ($file->isDir()) continue;
        $path=$file->getPathname();
        if ($relativePath) {
            $path=str_replace($dir,'',$path);
            $path=ltrim($path, '/');
        }
        $fileList[]=$path;
    }
    return $fileList;
}
echo json_encode(getDirContents('"""+dirx+"""'));"""
    return x
#
def file_get_contents(dirx):
    return f"""echo file_get_contents('{dirx}');"""
#}END.
