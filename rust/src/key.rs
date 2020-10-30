extern crate secp256k1;
extern crate rand;

use rand::rngs::OsRng;
use secp256k1::{Secp256k1, Message, SecretKey, PublicKey, Signature};
use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

pub struct Address {
    seck: String,
    // pubk: String,
}

impl Address {

    fn calculate_hash<T: Hash>(t: &T) -> u8 {
        let mut s = DefaultHasher::new();
        t.hash(&mut s);
        s.finish()
    }

    // pub fn f(s: &[u8]) -> &[u8] {
    //     &s
    // }

    pub fn gen_key() -> Address {

        let secp = Secp256k1::new();
        let mut rng = OsRng::new().expect("OsRng");
        let (secret_key, _public_key) = secp.generate_keypair(&mut rng);

        Address { seck: secret_key.to_string() }
    }

    pub fn sign_msg(&self, msg: String) -> String {
        let secp = Secp256k1::new();
        println!("{:?}", &msg.as_bytes());
        let message = Message::from_slice(&Address::calculate_hash(&msg)).expect("32 bytes");
        let secret_key = SecretKey::from_slice(&self.seck.as_bytes()).expect("32 bytes, within curve order");
        let sig = secp.sign(&message, &secret_key);

        sig.to_string()
    }

    pub fn verif_msg(&self, msg: String, sig: String) {
        let secp = Secp256k1::new();
        let message = Message::from_slice(&msg.as_bytes()).expect("32 bytes");
        let secret_key = SecretKey::from_slice(&self.seck.as_bytes()).expect("32 bytes, within curve order");
        let public_key = PublicKey::from_secret_key(&secp, &secret_key);
        let signature = Signature::from_compact(&sig.as_bytes()).expect("64 bytes");
        assert!(secp.verify(&message, &signature, &public_key).is_ok());
        println!("{:?}", secret_key.to_string());
    }
}

pub fn key() {
    let add = Address::gen_key();
    let sig = Address::sign_msg(&add, ("rishav raj").to_string());
    Address::verif_msg(&add, ("rishav raj").to_string(), sig);

}

// pub fn key() {

//     let secp = Secp256k1::new();
//     let mut rng = OsRng::new().expect("OsRng");
//     let (secret_key, public_key) = secp.generate_keypair(&mut rng);
//     let message = Message::from_slice(&[0xab; 32]).expect("32 bytes");

//     // Keypair { seck: secret_key, pubk: public_key };

//     println!("private key = {:?}", &secret_key.to_string());
//     println!("public key = {:?}", &public_key.to_string());
//     println!("message = {:?}", &message);

//     let sig = secp.sign(&message, &secret_key);
//     println!("message = {:?}", &sig.to_string());
//     assert!(secp.verify(&message, &sig, &public_key).is_ok());
// }

