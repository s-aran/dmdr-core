use std::collections::HashMap;

use rustpython_parser::ast::StmtClassDef;

pub struct Model<F>
where
    F: Filed,
{
    fields: HashMap<String, F>,
    meta: Meta,
}

#[derive(Debug)]
pub struct Attribute {
    key: String,
    value: String,
}

pub trait Filed {
    fn get_name(&self) -> &String;
    fn get_class_name(&self) -> &String;
    fn get_base_class_name(&self) -> &String;
    fn get_attributes(&self) -> &Vec<Attribute>;
}

#[derive(Debug)]
pub struct FieldInstance {
    name: String,
    class_name: String,
    base_class_name: String,
    attributes: Vec<Attribute>,
}

impl Filed for FieldInstance {
    fn get_name(&self) -> &String {
        &self.name
    }

    fn get_class_name(&self) -> &String {
        &self.class_name
    }

    fn get_base_class_name(&self) -> &String {
        &self.base_class_name
    }

    fn get_attributes(&self) -> &Vec<Attribute> {
        &self.attributes
    }
}

impl From<&StmtClassDef> for FieldInstance {
    fn from(value: &StmtClassDef) -> Self {
        let name = value.name.as_str().to_string();
        let class_name = value.name.as_str().to_string();

        let base_class_expr = value.bases.get(0).unwrap(); // first only
        let base_class = base_class_expr.as_attribute_expr().unwrap();
        let base_class_name_expr = base_class.value.as_name_expr().unwrap();
        let base_class_module_name = base_class_name_expr.id.as_str().to_string();
        let base_class_name = base_class.attr.as_str().to_string();

        println!("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~");
        println!("{:?}", value.body);
        println!("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~");

        Self {
            name,
            class_name,
            base_class_name: format!("{}.{}", base_class_module_name, base_class_name),
            attributes: Vec::new(),
        }
    }
}

pub struct Meta {
    // table_name ...
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_model_new() {
        let field = FieldInstance {
            name: "dummy".to_string(),
            class_name: "DummyModel".to_string(),
            base_class_name: "models.Model".to_string(),
            attributes: Vec::new(),
        };

        assert_eq!("dummy", field.get_name());
        assert_eq!("DummyModel", field.get_class_name());
        assert_eq!("models.Model", field.get_base_class_name());
        assert_eq!(0, field.get_attributes().len());
    }
}
