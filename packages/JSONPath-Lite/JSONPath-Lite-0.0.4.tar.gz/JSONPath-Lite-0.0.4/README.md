# jsonpath-lite
A very light weight utility which parses and uses JSONPath expressions for simple interactions with the Python data structures representing a JSON document.

## Usage
Say you have this JSON:
```
{
    "Things": [
        {
            "Name": "Thing1",
            "Value": "Dog"
        }
    ]
}
```
If you want to get the value of a Thing Named Thing1:  
`get_json_item(JSON Document, '$.Things[?Name="Thing1"].Value')`

If you want to update the value of the Thing Named Thing1 to Cat:  
`update_json_element(JSON Document, '$.Things[?Name="Thing1"].Value', 'Cat')`

If you want to add a new Thing:  
`write_new_json_element(JSON Document, '$.Things', {"Name": "Thing2", "Value": "Manbearpig"})`  
The arguments are: the JSON like object, path to the location of the new item, value of the new item, name of the new item.  
Note that a value is not supplied for newElementName since we are adding a new item to a list (array).

If you want to add a new field to one of the Things:  
`write_new_json_element(JSON Document, $.Things[?Name="Thing1"], True, "IsAGoodBoy")`

## Installation
With pip:
`pip install JSONPath-Lite`  
Otherwise you can just grab the JSONPathLite package from this repo and import it in your project. 

## Notes
This project came to be out of a need to find and manipulate specific pieces of data within a large highly nested JSON structure. As such, it is designed to stop searching and return the first match for a given path. The functionality of returning all matches for a given path will be added at some point in the future. 
