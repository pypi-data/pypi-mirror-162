<p align="center">
    <img  width="50%" height="50%" src="https://snowmate-prod-assets.s3.amazonaws.com/Snowmate+logo+black+no+solgan.svg">
</p>

# Code Discovery

### Snowmate’s public code discovery tools repository 🔧

##### code_discovery scans you project's code and checks what libraries you import in it.
##### Why not use requirements.txt? Becuase you may use different libraries from the [Python Standard Library](https://docs.python.org/3/library/), which
##### are not needed in the requirements.txt.

### Installation

    $ pip3 install code-discovery

### Usage
  
To discover imports and echo the output to the console:

    $ code_discovery imports -p {project_root_path}
    
    
To discover imports and save output to a file:
    
    $ code_discovery imports -p {project_root_path} -o {output_full_path}

### Testing


    $ pytest .

### License

[Apache License 2.0](https://github.com/snowmate/code-discovery/blob/master/LICENSE)
