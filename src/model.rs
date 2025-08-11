use ahash::AHashMap;
use serde::Deserialize;
use std::sync::Arc;

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct SourceCode {
    pub source_file: String,
    pub partial: Vec<String>,
    pub line_number: usize,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct MetaData {
    pub uuid: String,
    // source: Any
    pub code: SourceCode,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct MyField {
    pub name: String,
    pub column: String,
    pub attname: String,
    pub verbose_name: String,
    pub help_text: String,

    pub related_model: Option<MetaData>,
    pub validators: Vec<String>,

    pub null: bool,

    pub _meta_data: MetaData,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct MyModel {
    pub app_label: String,
    pub db_table: String,
    pub model_name: String,
    pub object_name: String,

    #[serde(default)]
    pub local_fields: Vec<MyField>,
    #[serde(default, alias = "related_fields", alias = "relation_fields")]
    pub relation_fields: Vec<MyField>,
    #[serde(default, alias = "forwarded_fields", alias = "forward_fields")]
    pub forward_fields: Vec<MyField>,

    pub _meta_data: MetaData,
}

impl MyModel {
    pub fn all_fields(&self) -> impl Iterator<Item = &MyField> {
        self.local_fields
            .iter()
            .chain(self.relation_fields.iter())
            .chain(self.forward_fields.iter())
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub enum RelationType {
    ForeignKey,
    OneToOne,
    ManyToMany,
}

impl From<&str> for RelationType {
    fn from(value: &str) -> Self {
        match value {
            "ForeignKey" => RelationType::ForeignKey,
            "OneToOne" => RelationType::OneToOne,
            "ManyToMany" => RelationType::ManyToMany,
            _ => panic!("Invalid relation type"),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct Relation {
    pub src_model_uuid: String,
    pub src_model: String,
    pub src_field_uuid: String,
    pub src_field: String,
    pub target_model_uuid: String,
    pub target_model: String,
    pub relation_type: RelationType,
    pub through_model_uuid: Option<String>,
    pub through_model: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct Structure {
    pub models: Vec<MyModel>,
    pub relations: Vec<Relation>,
}

#[derive(Clone, Debug)]
pub struct UuidIndexes {
    model_map: AHashMap<String, Arc<MyModel>>,
    field_map: AHashMap<String, Arc<MyField>>,
    field_model: AHashMap<String, String>,
    src_field_rels: AHashMap<String, Arc<Relation>>,
    target_model_rels: AHashMap<String, Arc<Relation>>,
}

impl UuidIndexes {
    /// build indexes
    pub fn new(shared: &Arc<Structure>) -> Self {
        let mut model_map = AHashMap::new();
        let mut field_map = AHashMap::new();
        let mut field_model = AHashMap::new();
        let mut src_field_rels = AHashMap::new();
        let mut target_model_rels = AHashMap::new();

        // models
        for model in &shared.models {
            let m_uuid = model._meta_data.uuid.clone();
            let arc_model = Arc::new(model.clone());
            model_map.insert(m_uuid.clone(), Arc::clone(&arc_model));

            // for field in &model.fields {
            for field in model.all_fields() {
                let f_uuid = field._meta_data.uuid.clone();
                let arc_field = Arc::new(field.clone());
                field_map.insert(f_uuid.clone(), Arc::clone(&arc_field));
                field_model.insert(f_uuid, m_uuid.clone());
            }
        }

        // relations
        for rel in &shared.relations {
            let arc_rel = Arc::new(rel.clone());
            src_field_rels.insert(rel.src_field.clone(), Arc::clone(&arc_rel));
            target_model_rels.insert(rel.target_model.clone(), Arc::clone(&arc_rel));
        }

        UuidIndexes {
            model_map,
            field_map,
            field_model,
            src_field_rels,
            target_model_rels,
        }
    }

    pub fn has_model_name(&self, name: &str) -> bool {
        self.model_map
            .values()
            .any(|model| model.model_name == name)
    }

    pub fn has_model(&self, uuid: &str) -> bool {
        self.model_map.contains_key(uuid)
    }

    pub fn has_field(&self, uuid: &str) -> bool {
        self.field_map.contains_key(uuid)
    }

    pub fn has_source_field(&self, uuid: &str) -> bool {
        self.src_field_rels.contains_key(uuid)
    }

    pub fn has_target_model(&self, uuid: &str) -> bool {
        self.target_model_rels.contains_key(uuid)
    }

    /// get model objects
    pub fn get_models(&self) -> Vec<Arc<MyModel>> {
        self.model_map.values().cloned().collect()
    }

    // get field objects
    pub fn get_fields(&self) -> Vec<Arc<MyField>> {
        self.field_map.values().cloned().collect()
    }

    /// get model object from uuid
    pub fn get_model(&self, uuid: &str) -> Arc<MyModel> {
        Arc::clone(self.model_map.get(uuid).unwrap())
    }

    pub fn get_model_by_name(&self, name: &str) -> Arc<MyModel> {
        Arc::clone(
            self.model_map
                .values()
                .find(|model| model.model_name == name)
                .unwrap(),
        )
    }

    /// get field object from uuid
    pub fn get_field(&self, uuid: &str) -> Arc<MyField> {
        Arc::clone(
            self.field_map
                .get(uuid)
                .unwrap_or_else(|| panic!("unknown field uuid `{}`", uuid)),
        )
    }

    /// get model's uuid from field's uuid
    pub fn get_model_from_field(&self, uuid: &str) -> &str {
        self.field_model
            .get(uuid)
            .map(|s| s.as_str())
            .unwrap_or_else(|| panic!("unknown field→model mapping for `{}`", uuid))
    }

    /// get relation object from source field's uuid
    pub fn get_src_field_relation(&self, uuid: &str) -> Arc<Relation> {
        Arc::clone(
            self.src_field_rels
                .get(uuid)
                .unwrap_or_else(|| panic!("unknown src_field relation for `{}`", uuid)),
        )
    }

    /// get relation object from target field's uuid
    pub fn get_target_model_relation(&self, uuid: &str) -> Arc<Relation> {
        Arc::clone(
            self.target_model_rels
                .get(uuid)
                .unwrap_or_else(|| panic!("unknown target_model relation for `{}`", uuid)),
        )
    }
}
