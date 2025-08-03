use ahash::AHashMap;
use serde::Deserialize;
use std::sync::Arc;

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct SourceCode {
    pub source_file: String,
    pub partial: String,
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
    pub fields: Vec<MyField>,

    pub _meta_data: MetaData,
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
pub struct RelationOld {
    pub src_field: MyField,
    pub target_model: MyModel,
    pub relation_type: RelationType,
    pub through_field: Option<MyField>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct Relation {
    pub src_field: String,
    pub target_model: String,
    pub relation_type: RelationType,
    pub through_field: Option<String>,
}

impl From<RelationOld> for Relation {
    fn from(value: RelationOld) -> Self {
        Self {
            src_field: value.src_field._meta_data.uuid,
            target_model: value.target_model._meta_data.uuid,
            relation_type: value.relation_type,
            through_field: value.through_field.map(|f| f._meta_data.uuid),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub(crate) struct StructureOld {
    pub models: Vec<MyModel>,
    pub relations: Vec<RelationOld>,
}

#[derive(Debug, Clone, PartialEq, Eq, Deserialize)]
pub struct Structure {
    pub models: Vec<MyModel>,
    pub relations: Vec<Relation>,
}

impl From<StructureOld> for Structure {
    fn from(value: StructureOld) -> Self {
        Self {
            models: value.models,
            relations: value.relations.into_iter().map(|r| r.into()).collect(),
        }
    }
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

            for field in &model.fields {
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

    /// get model object from uuid
    pub fn get_model(&self, uuid: &str) -> Arc<MyModel> {
        Arc::clone(self.model_map.get(uuid).unwrap())
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
