mod model;

use std::io::Read;
use std::{fs::File, path::Path};

use rustpython_parser::{Mode, parse};

fn main() {
    let path_str = r#"django-tutorial-master/mysite/polls/models.py"#;
    let path = Path::new(path_str);

    let mut file = match File::open(path) {
        Ok(f) => f,
        Err(e) => {
            eprintln!("{}", e);
            return;
        }
    };

    let mut buf = String::new();
    match file.read_to_string(&mut buf) {
        Ok(s) => {
            println!("{} bytes read.", s);
        }
        Err(e) => {
            eprintln!("{}", e);
            return;
        }
    };

    let base_path = Path::new(r#"django-tutorial-master/mysite/polls"#);
    let result = parse(buf.as_str(), Mode::Module, "<embedded>");

    for e in result.iter() {
        println!("{:?}", e);
    }
}
