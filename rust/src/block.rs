// use chrono::prelude::*;
use serde_json::json;
// use hex_literal::hex;
use sha2::{Sha256, Digest};

pub struct Block {
    hsh: String,
    time: String,
    prev_hsh: String,
    mrkl_rt: String,
    ht: i8,
    ver: String,
    size: u64,
}

pub fn hex_string(input: &[u8]) -> String {
    input.as_ref().iter().map(|b| format!("{:x}", b)).collect()
}

impl Block {

    //construct
    pub fn new(hsh: &str, time:&str, prev_hsh: &str, mrkl_rt: &str, ht: i8, ver: &str, size: u64) -> Block {
        Block {
            hsh: hsh.to_string(),
            time: time.to_string(),
            prev_hsh: prev_hsh.to_string(),
            mrkl_rt: mrkl_rt.to_string(),
            ht: ht,
            ver: ver.to_string(),
            size: size,
        }
    }

    

    pub fn add_prev_hsh(&mut self) {
        self.prev_hsh = String::from("jasffgajflhif")
    }

    pub fn to_json(&self) -> String {
        let new = json!({
            "hsh" : self.hsh,
            "time" : self.time,
            "prev_hsh" : self.prev_hsh,
            "mrkl_rt" : self.mrkl_rt,
            "ht" : self.ht,
            "ver" : self.ver,
            "size" : self.size
        });

        new.to_string()
    }

    pub fn calc_hsh(&mut self) {
        let new = json!({
            "time" : self.time,
            "prev_hsh" : self.prev_hsh,
            "mrkl_rt" : self.mrkl_rt,
            "ht" : self.ht,
            "ver" : self.ver,
            "size" : self.size
        });

        // create a Sha256 object
        let mut hasher = Sha256::new();

        // write input message
        hasher.update(new.to_string().as_bytes());

        // read hash digest and consume hasher
        let result = hasher.finalize();

        let hex = hex_string(&result);

        self.hsh = hex;
    }
}

pub fn block_test() {
    let mut blk = Block::new("hsgh", "1234", "", "mrkl", 90, "0.1.0", 234567);
    blk.add_prev_hsh();
    blk.calc_hsh();
    let out = blk.to_json();
    println!("{:?}", out);
}