use std::collections::HashMap;

pub struct Model<F>
where
    F: Filed,
{
    fields: HashMap<String, F>,
    meta: Meta,
}

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
