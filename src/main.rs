mod model;

use std::io::Read;
use std::{fs::File, path::Path};

use model::FieldInstance;
use rustpython_parser::ast::StmtClassDef;
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
        // println!("{:?}", e);

        if !e.is_module() {
            break;
        }

        let module = e.as_module().unwrap();

        println!(
            "--------------------------------------------------------------------------------"
        );

        // println!("{:?}", module.body);

        let module_body = &module.body;

        for e in module_body.iter() {
            // println!("{:?}", e);

            if !e.is_class_def_stmt() {
                continue;
            }

            println!("============================================================");

            let class = e.as_class_def_stmt().unwrap();
            println!("{:?}", class);

            for c in class.body.iter() {
                println!("{:?}", c);
            }

            let a: FieldInstance = From::from(class);

            println!("============================================================");
        }

        println!(
            "--------------------------------------------------------------------------------"
        );
    }
}
