#[cfg(target_os = "linux")]
fn main() {
    println!("cargo:rustc-link-lib=pcre");
}

#[cfg(target_os = "macos")]
fn main() {
    unimplemented!();
}
