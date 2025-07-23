# PIIInspector
Tool to inspect folders/files for potential PII information

## Customise

It's likely that you might have several different use cases. For each use case create a copy of the file piiInspector.py and edit specifically for what you need.

Edit the array IGNORE_FILE_EXTENSIONS to include any file extension that you want to ignore.  For example, if the list contained '.jpg' then any file with that extension will not be inspected.

To look for specific patterns in files, edit the list PATTERNS.  Each pattern contains a title and a regex pattern, e.g "Your Pattern Name": r"your_regex_pattern".
Learn more about regex patters here https://coderpad.io/blog/development/the-complete-guide-to-regular-expressions-regex/.

To ingore specific patterns edit IGNORE_PATTERNS_FOR_MATCH.  For example you may have an "Email Address" inspector in PATTERNS.  But you might have added in some dummy/fake email addresses already, like johndoe@john.com, ideally we dont want this tool to report those dummy values.  Edit IGNORE_PATTERNS_FOR_MATCH to contain a matching title "Email Address" and list containing the string to ignore, e.g "johndoe@john.com".  Check out the code for more examples.

Edit IGNORE_FOLDERS to ingore certain foles.

## Run

chmod +x piiInspector.py

./piiInspector.py ...folder to inspect....
