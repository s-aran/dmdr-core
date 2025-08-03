pub mod model;

use std::path::PathBuf;
use std::sync::Arc;
use std::{error::Error, fs};

use crate::model::{Structure, StructureOld, UuidIndexes};

pub fn load_json(file_path: PathBuf) -> Result<(Arc<Structure>, UuidIndexes), Box<dyn Error>> {
    let mut content = fs::read_to_string(file_path).expect("unexepceted filesystem error");
    let data_old: StructureOld =
        unsafe { simd_json::serde::from_str(&mut content).expect("unexepceted json error") };
    let data: Structure = data_old.into();

    let shared = Arc::new(data);
    let indexes = UuidIndexes::new(&Arc::clone(&shared));

    // let f = indexes.get_field("b8b36a2a-89fd-4773-9c04-9914afcc2aa9");
    // let m_uuid = indexes.get_model_from_field(&f._meta_data.uuid);
    // let m = indexes.get_model(m_uuid);

    Ok((shared, indexes))
}
