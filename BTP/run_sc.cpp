//
//  main.cpp
//  run_scripts
//
//  Created by Vatsal Chanana on 26/05/16.
//  Copyright (c) 2016 Vatsal. All rights reserved.
//

#include <iostream>
#include<fstream>
#include<cstdio>
#include<vector>

using namespace std;

int main()
{
   system("export LANG=en_US.UTF-8");
    
    system("export LC_ALL=en_US.UTF-8");
    for(int i=80;i<110;i++)
    {
        string file_name = "/Users/vatsalchanana/Documents/FinalData/scriptgen/output_rem"+to_string(i+1)+".json.gz";
        string cmd = "python /Users/vatsalchanana/Desktop/BTP/BTP/load_products.py ";
        system((cmd+file_name).c_str());
    }
    return 0;
}