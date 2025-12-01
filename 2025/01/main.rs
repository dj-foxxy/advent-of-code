use clap::Parser;
use std::fs::File;
use std::io::{self, BufRead, BufReader, Lines};
use std::path::Path;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    #[arg()]
    input: String,
}

fn read_lines<P>(path: P) -> io::Result<io::Lines<io::BufReader<File>>>
where
    P: AsRef<Path>,
{
    Ok(io::BufReader::new(File::open(path)?).lines())
}

fn parse_direction(line: &String) -> Option<i32> {
    Some(match line.chars().nth(0)? {
        'L' => -1,
        'R' => 1,
        _ => return None,
    })
}

fn parse_steps(line: &String) -> Option<i32> {
    match line.get(1..)?.parse::<i32>() {
        Ok(steps) => Some(steps),
        Err(_) => None,
    }
}

fn parse_instruction(line: &String) -> Option<i32> {
    Some(parse_direction(line)? * parse_steps(line)?)
}

fn parse_instructions(lines: Lines<BufReader<File>>) -> Option<i32> {
    let mut current = 50;
    let mut password = 0;

    for wrapped_line in lines {
        let line = match wrapped_line {
            Ok(line) => line,
            Err(_) => return None,
        };

        current += parse_instruction(&line)?;

        if current == 0 {
            password += 1;
        }
    }

    Some(password)
}

fn main() {
    let args = Args::parse();

    let lines = match read_lines(args.input) {
        Ok(lines) => lines,
        Err(_) => {
            eprintln!("Cannot open input file");
            std::process::exit(1);
        }
    };

    match parse_instructions(lines) {
        Some(password) => println!("{}", password),
        None => {
            eprintln!("Cannot parse input file");
            std::process::exit(1);
        }
    };
}
