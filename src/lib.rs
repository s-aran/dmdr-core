pub mod model;

use std::path::PathBuf;
use std::sync::Arc;
use std::{error::Error, fs};

use serde::de;

use crate::model::{Structure, UuidIndexes};

fn get_json<'a, T>(content: &'a str) -> T
where
    T: de::Deserialize<'a>,
{
    #[cfg(feature = "release-deps")]
    unsafe {
        simd_json::serde::from_str(&mut content).expect("unexepceted json error")
    }

    #[cfg(not(feature = "release-deps"))]
    serde_json::from_str(content).expect("unexepceted json error")
}

pub fn load_json(file_path: PathBuf) -> Result<(Arc<Structure>, UuidIndexes), Box<dyn Error>> {
    let content = fs::read_to_string(file_path).expect("unexepceted filesystem error");
    let data: Structure = get_json(content.as_str());
    let shared = Arc::new(data);
    let indexes = UuidIndexes::new(&Arc::clone(&shared));

    // let f = indexes.get_field("b8b36a2a-89fd-4773-9c04-9914afcc2aa9");
    // let m_uuid = indexes.get_model_from_field(&f._meta_data.uuid);
    // let m = indexes.get_model(m_uuid);

    Ok((shared, indexes))
}
