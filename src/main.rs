use std::fmt;
use std::io;
// use rand::seq::SliceRandom;

macro_rules! parse_input {
    ($x:expr, $t:ident) => {
        $x.trim().parse::<$t>().unwrap()
    };
}

// Coordinate

#[derive(Debug)]
struct Coordinate {
    x: i32,
    y: i32,
}

impl Coordinate {
    // Another associated function, taking two arguments:
    fn new(x: i32, y: i32) -> Coordinate {
        Coordinate { x: x, y: y }
    }

    fn euclidean_distance(&self, other: &Self) -> f64 {
        (((self.x - other.x).pow(2) - (self.y - other.y).pow(2)) as f64).sqrt()
    }
}

impl fmt::Display for Coordinate {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Coordinate(x={}, y={})", self.x, self.y)
    }
}

impl PartialEq for Coordinate {
    fn eq(&self, other: &Self) -> bool {
        self.x == other.x && self.y == other.y
    }
}

// -----------------

// Speed Vector

#[derive(Debug)]
struct SpeedVector {
    vx: i32,
    vy: i32,
}

impl SpeedVector {
    fn new(vx: i32, vy: i32) -> SpeedVector {
        SpeedVector { vx: vx, vy: vy }
    }

    fn absolute_speed(&self) -> f64 {
        (((self.vx).pow(2) + (self.vy).pow(2)) as f64).sqrt()
    }
}

impl fmt::Display for SpeedVector {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "SpeedVector(vx={}, vy={})", self.vx, self.vy)
    }
}

impl PartialEq for SpeedVector {
    fn eq(&self, other: &Self) -> bool {
        self.vx == other.vx && self.vy == other.vy
    }
}

// -----------------

#[derive(Debug)]
struct Unit {
    unit_id: i32,
    unit_type: i32,
    player_id: i32,
    mass: f64,
    radius: i32,
    coordinate: Coordinate,
    speed: SpeedVector,
}

impl Unit {
    fn new(
        unit_id: i32,
        unit_type: i32,
        player_id: i32,
        mass: f64,
        radius: i32,
        x: i32,
        y: i32,
        vx: i32,
        vy: i32,
    ) -> Unit {
        Unit {
            unit_id: unit_id,
            unit_type: unit_type,
            player_id: player_id,
            mass: mass,
            radius: radius,
            coordinate: Coordinate::new(x, y),
            speed: SpeedVector::new(vx, vy),
        }
    }
}

// ------------------

///
/// Possible actions:
/// - harvest water from wrecks
/// - create tar pools - increase mass and make tankers indestructible
///
#[derive(Debug)]
struct Reaper {
    unit: Unit,
    friction: f64,
}

impl Reaper {
    fn new(
        unit_id: i32,
        unit_type: i32,
        player_id: i32,
        mass: f64,
        radius: i32,
        x: i32,
        y: i32,
        vx: i32,
        vy: i32,
    ) -> Reaper {
        let inner_unit = Unit::new(unit_id, unit_type, player_id, mass, radius, x, y, vx, vy);
        Reaper {
            unit: inner_unit,
            friction: 0.2,
        }
    }
}

impl fmt::Display for Reaper {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "Reaper(id={}, mass={}, radius={}, coordinate={}, speed={})",
            self.unit.unit_id,
            self.unit.mass,
            self.unit.radius,
            self.unit.coordinate,
            self.unit.speed,
        )
    }
}

// ------------------

///
/// Potential actions:
/// - destroy tankers (to create wrecks)
/// - throw nitro grenade (to push looters in a radius of 1000)
///
#[derive(Debug)]
struct Destroyer {
    unit: Unit,
    friction: f64,
}

impl Destroyer {
    fn new(
        unit_id: i32,
        unit_type: i32,
        player_id: i32,
        mass: f64,
        radius: i32,
        x: i32,
        y: i32,
        vx: i32,
        vy: i32,
    ) -> Destroyer {
        let inner_unit = Unit::new(unit_id, unit_type, player_id, mass, radius, x, y, vx, vy);
        Destroyer {
            unit: inner_unit,
            friction: 0.3,
        }
    }
}

impl fmt::Display for Destroyer {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "Destroyer(id={}, mass={}, radius={}, coordinate={}, speed={})",
            self.unit.unit_id,
            self.unit.mass,
            self.unit.radius,
            self.unit.coordinate,
            self.unit.speed,
        )
    }
}

// ------------------

///
/// Generates rage proportional to its speed
///
/// Potential actions
/// - creates oil pools (removes friction and prevents harvesting of wrecks)
///
#[derive(Debug)]
struct Doof {
    unit: Unit,
    friction: f64,
}

impl Doof {
    fn new(
        unit_id: i32,
        unit_type: i32,
        player_id: i32,
        mass: f64,
        radius: i32,
        x: i32,
        y: i32,
        vx: i32,
        vy: i32,
    ) -> Doof {
        let inner_unit = Unit::new(unit_id, unit_type, player_id, mass, radius, x, y, vx, vy);
        Doof {
            unit: inner_unit,
            friction: 0.25,
        }
    }
}

impl fmt::Display for Doof {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "Doof(id={}, mass={}, radius={}, coordinate={}, speed={})",
            self.unit.unit_id,
            self.unit.mass,
            self.unit.radius,
            self.unit.coordinate,
            self.unit.speed,
        )
    }
}

// ------------------

#[derive(Debug)]
struct Tanker {
    unit: Unit,
    friction: f64,
    throttle: f64,
    water_quantity: i32,
    water_capacity: i32,
}

impl Tanker {
    fn new(
        unit_id: i32,
        unit_type: i32,
        player_id: i32,
        mass: f64,
        radius: i32,
        x: i32,
        y: i32,
        vx: i32,
        vy: i32,
        extra: i32,
        extra_2: i32,
    ) -> Tanker {
        let inner_unit = Unit::new(unit_id, unit_type, player_id, mass, radius, x, y, vx, vy);
        Tanker {
            unit: inner_unit,
            friction: 0.4,
            water_quantity: extra,
            water_capacity: extra_2,
            throttle: 2.5 + 0.5 * (extra as f64),
        }
    }
}

impl fmt::Display for Tanker {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "Wreck(id={}, mass={}, radius={}, coordinate={}, speed={}, water_quantity={}, water_capacity={})",
            self.unit.unit_id,
            self.unit.mass,
            self.unit.radius,
            self.unit.coordinate,
            self.unit.speed,
            self.water_quantity,
            self.water_capacity,
        )
    }
}

// ------------------

#[derive(Debug)]
struct Wreck {
    unit: Unit,
    water_quantity: i32,
}

impl Wreck {
    fn new(
        unit_id: i32,
        unit_type: i32,
        player_id: i32,
        mass: f64,
        radius: i32,
        x: i32,
        y: i32,
        vx: i32,
        vy: i32,
        extra: i32,
    ) -> Wreck {
        let inner_unit = Unit::new(unit_id, unit_type, player_id, mass, radius, x, y, vx, vy);
        Wreck {
            unit: inner_unit,
            water_quantity: extra,
        }
    }
}

// To use the `{}` marker, the trait `fmt::Display` must be implemented
// manually for the type.
impl fmt::Display for Wreck {
    // This trait requires `fmt` with this exact signature.
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // Write strictly the first element into the supplied output
        // stream: `f`. Returns `fmt::Result` which indicates whether the
        // operation succeeded or failed. Note that `write!` uses syntax which
        // is very similar to `println!`.
        write!(
            f,
            "Wreck(id={}, mass={}, radius={}, coordinate={}, speed={}, water_quantity={})",
            self.unit.unit_id,
            self.unit.mass,
            self.unit.radius,
            self.unit.coordinate,
            self.unit.speed,
            self.water_quantity
        )
    }
}

// ------------------

#[derive(Debug)]
struct TarPool {
    unit: Unit,
}

impl TarPool {
    fn new(
        unit_id: i32,
        unit_type: i32,
        player_id: i32,
        mass: f64,
        radius: i32,
        x: i32,
        y: i32,
        vx: i32,
        vy: i32,
    ) -> TarPool {
        let inner_unit = Unit::new(unit_id, unit_type, player_id, mass, radius, x, y, vx, vy);
        TarPool { unit: inner_unit }
    }
}

impl fmt::Display for TarPool {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "TarPool(id={}, mass={}, radius={}, coordinate={}, speed={})",
            self.unit.unit_id,
            self.unit.mass,
            self.unit.radius,
            self.unit.coordinate,
            self.unit.speed,
        )
    }
}

// ------------------

struct OilPool {
    unit: Unit,
}

impl OilPool {
    fn new(
        unit_id: i32,
        unit_type: i32,
        player_id: i32,
        mass: f64,
        radius: i32,
        x: i32,
        y: i32,
        vx: i32,
        vy: i32,
    ) -> OilPool {
        let inner_unit = Unit::new(unit_id, unit_type, player_id, mass, radius, x, y, vx, vy);
        OilPool { unit: inner_unit }
    }
}

impl fmt::Display for OilPool {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "OilPool(id={}, mass={}, radius={}, coordinate={}, speed={})",
            self.unit.unit_id,
            self.unit.mass,
            self.unit.radius,
            self.unit.coordinate,
            self.unit.speed,
        )
    }
}

// ------------------

fn find_doof_target(player_doof_ref: Option<&Doof>, destoyers: Vec<&Destroyer>) -> Coordinate {
    // let closest_destroyer_index = destoyers
    //     .iter()
    //     .enumerate()
    //     .min_by_key(|(_, &destroyer)| {
    //         let distance = destroyer.unit.coordinate.euclidean_distance(player_doof_coordinate);
    //         distance.partial_cmp(&f64::MIN).expect("we can't consume NaN values here")
    //     })
    //     .expect("The vector is empty")
    //     .0;

    let player_doof_coordinate = match player_doof_ref {
        Some(doof_ref) => &doof_ref.unit.coordinate,
        None => {
            eprintln!("the player's doof was not initialized");
            let chosen_destroyer = destoyers
                .iter()
                .find(|&destroyer| destroyer.unit.player_id != 0)
                .expect("this should never happen");
            return Coordinate::new(
                chosen_destroyer.unit.coordinate.x,
                chosen_destroyer.unit.coordinate.y,
            );
        }
    };

    // let player_doof_coordinate = &player_doof_ref.expect("No value available").unit.coordinate;
    let fartest_destroyer_index = destoyers
        .iter()
        .enumerate()
        .max_by_key(|(_, &destroyer)| {
            let distance = destroyer
                .unit
                .coordinate
                .euclidean_distance(&player_doof_coordinate) as i32;
            distance
        })
        .expect("The vector is empty")
        .0;

    Coordinate::new(
        destoyers[fartest_destroyer_index].unit.coordinate.x,
        destoyers[fartest_destroyer_index].unit.coordinate.y,
    )
}

/// prints the action for destroyer at the end of the round
fn destroyer_decider(
    my_rage: &i32,
    chosen_tanker: &Coordinate,
    my_doof: Option<&Doof>,
    my_destroyer: Option<&Destroyer>,
    reapers: Vec<Reaper>,
    destroyers: Vec<Destroyer>,
) -> () {
    let doof_coordinate = match my_doof {
        Some(doof_ref) => &doof_ref.unit.coordinate,
        None => {
            eprintln!("the player's doof was not initialized");
            println!("{} {} 200 Destroyer", chosen_tanker.x, chosen_tanker.y);
            return;
        }
    };
    let destroyer_coordinate = match my_destroyer {
        Some(destroyer_ref) => &destroyer_ref.unit.coordinate,
        None => {
            eprintln!("the player's doof was not initialized");
            println!("{} {} 200 Destroyer", chosen_tanker.x, chosen_tanker.y);
            return;
        }
    };

    if my_rage < &45 {
        println!("{} {} 200 Destroyer", chosen_tanker.x, chosen_tanker.y);
        return;
    }

    eprintln!("rage limit reached: {}", my_rage);

    for reaper in reapers.iter() {
        if reaper.unit.player_id == 0 {
            continue;
        }
        if reaper
            .unit
            .coordinate
            .euclidean_distance(&destroyer_coordinate)
            < 1000_f64
        {
            // TODO: this stops on the first iteration where the distance is fulfilled
            println!(
                "SKILL {} {} Destroyer",
                reaper.unit.coordinate.x, reaper.unit.coordinate.y
            );
            return;
        }
    }

    for destroyer in destroyers.iter() {
        if destroyer.unit.player_id == 0 {
            continue;
        }
        if destroyer
            .unit
            .coordinate
            .euclidean_distance(&destroyer_coordinate)
            < 1000_f64
        {
            println!(
                "SKILL {} {} Destroyer",
                destroyer.unit.coordinate.x, destroyer.unit.coordinate.y
            );
            return;
        }
    }

    eprintln!("Distance too far");
    println!("{} {} 200 Destroyer", chosen_tanker.x, chosen_tanker.y);
}

/**
 * Auto-generated code below aims at helping you parse
 * the standard input according to the problem statement.
 **/
fn main() {
    let mut round_nr = 0;

    // game loop
    loop {
        round_nr += 1;
        let mut input_line = String::new();
        io::stdin().read_line(&mut input_line).unwrap();
        let my_score = parse_input!(input_line, i32);
        let mut input_line = String::new();
        io::stdin().read_line(&mut input_line).unwrap();
        let enemy_score_1 = parse_input!(input_line, i32);
        let mut input_line = String::new();
        io::stdin().read_line(&mut input_line).unwrap();
        let enemy_score_2 = parse_input!(input_line, i32);
        let mut input_line = String::new();
        io::stdin().read_line(&mut input_line).unwrap();
        let my_rage = parse_input!(input_line, i32);
        let mut input_line = String::new();
        io::stdin().read_line(&mut input_line).unwrap();
        let enemy_rage_1 = parse_input!(input_line, i32);
        let mut input_line = String::new();
        io::stdin().read_line(&mut input_line).unwrap();
        let enemy_rage_2 = parse_input!(input_line, i32);
        let mut input_line = String::new();
        io::stdin().read_line(&mut input_line).unwrap();
        let unit_count = parse_input!(input_line, i32);

        let mut reapers: Vec<Reaper> = vec![];
        let mut destroyers: Vec<Destroyer> = vec![];
        let mut doofs: Vec<Doof> = vec![];
        let mut tankers: Vec<Tanker> = vec![];
        let mut wrecks: Vec<Wreck> = vec![];
        let mut tar_pools: Vec<TarPool> = vec![];
        let mut oil_pools: Vec<OilPool> = vec![];

        let mut my_reaper: Option<Reaper> = None;
        let mut my_doof: Option<Doof> = None;
        let mut my_destroyer: Option<Destroyer> = None;

        let mut wreck_coordinates: Vec<Coordinate> = vec![];
        let mut tanker_coordinates: Vec<Coordinate> = vec![];
        let mut max_water = 0;
        let mut max_tanker_water = 0;
        let mut chosen_wreck: &Coordinate = &Coordinate::new(0, 0);
        let mut chosen_tanker: &Coordinate = &Coordinate::new(0, 0);
        let mut max_water_x = 0;
        let mut max_water_y = 0;
        let mut max_tanker_water_x = 0;
        let mut max_tanker_water_y = 0;

        for i in 0..unit_count as usize {
            let mut input_line = String::new();
            io::stdin().read_line(&mut input_line).unwrap();
            let inputs = input_line.split(" ").collect::<Vec<_>>();
            let unit_id = parse_input!(inputs[0], i32);
            let unit_type = parse_input!(inputs[1], i32);
            let player = parse_input!(inputs[2], i32);
            let mass = parse_input!(inputs[3], f64);
            let radius = parse_input!(inputs[4], i32);
            let x = parse_input!(inputs[5], i32);
            let y = parse_input!(inputs[6], i32);
            let vx = parse_input!(inputs[7], i32);
            let vy = parse_input!(inputs[8], i32);
            let extra = parse_input!(inputs[9], i32);
            let extra_2 = parse_input!(inputs[10], i32);

            // todo: do this with a match
            match unit_type {
                0 => {
                    let current_reaper =
                        Reaper::new(unit_id, unit_type, player, mass, radius, x, y, vx, vy);
                    reapers.push(current_reaper);
                    if player == 0 {
                        my_reaper = Some(Reaper::new(
                            unit_id, unit_type, player, mass, radius, x, y, vx, vy,
                        ));
                        eprintln!("Player's destroyer found: {:?}", &my_reaper);
                    }
                }
                1 => {
                    let current_destroyer =
                        Destroyer::new(unit_id, unit_type, player, mass, radius, x, y, vx, vy);
                    destroyers.push(current_destroyer);
                    if player == 0 {
                        my_destroyer = Some(Destroyer::new(
                            unit_id, unit_type, player, mass, radius, x, y, vx, vy,
                        ));
                        eprintln!("Player's destroyer found: {:?}", &my_destroyer);
                    }
                }
                2 => {
                    let current_doof =
                        Doof::new(unit_id, unit_type, player, mass, radius, x, y, vx, vy);
                    // eprintln!("[DEBUG] Doof data : {:?}", &current_doof);
                    doofs.push(current_doof);
                    if player == 0 {
                        my_doof = Some(Doof::new(
                            unit_id, unit_type, player, mass, radius, x, y, vx, vy,
                        ));
                        eprintln!("Player's doof found: {:?}", &my_doof);
                    }
                }
                3 => {
                    let current_tanker = Tanker::new(
                        unit_id, unit_type, player, mass, radius, x, y, vx, vy, extra, extra_2,
                    );
                    tankers.push(current_tanker);
                }
                4 => {
                    let current_wreck = Wreck::new(
                        unit_id, unit_type, player, mass, radius, x, y, vx, vy, extra,
                    );
                    wrecks.push(current_wreck);
                }
                5 => {
                    let tar_pool =
                        TarPool::new(unit_id, unit_type, player, mass, radius, x, y, vx, vy);
                    tar_pools.push(tar_pool);
                }
                6 => {
                    let oil_pool =
                        OilPool::new(unit_id, unit_type, player, mass, radius, x, y, vx, vy);
                    oil_pools.push(oil_pool);
                }
                _ => (),
            };
        }

        // eprintln!("Wreck positions: {:?}", wreck_coordinates);
        // eprintln!("Tanker positions: {:?}", tanker_coordinates);

        // eprintln!("Wreck objects: {:?}", wrecks);
        // eprintln!("Tanker objects: {:?}", tankers);
        // eprintln!("Reaper objects: {:?}", reapers);
        // eprintln!("Destroyer objects: {:?}", destroyers);
        // eprintln!("Doof objects: {:?}", doofs);

        // Write an action using println!("message...");
        // To debug: eprintln!("Debug message...");

        let doof_target: Coordinate =
            find_doof_target(my_doof.as_ref(), destroyers.iter().skip(1).collect());
        // Reaper

        let my_reaper_speed = &my_reaper.as_ref().expect("No Reaper").unit.speed;
        let selected_x = (chosen_wreck.x as f64 - (my_reaper_speed.vx as f64 * 1.5)) as i32;
        let selected_y = (chosen_wreck.y as f64 - (my_reaper_speed.vy as f64 * 1.5)) as i32;

        eprintln!(
            "Round: {}, speed: {} - i.e. {}, position: {}, ({}, {})",
            round_nr,
            my_reaper_speed,
            my_reaper_speed.absolute_speed(),
            my_reaper.as_ref().expect("No Reaper").unit.coordinate,
            selected_x,
            selected_y
        );

        if round_nr < 3 {
            println!("{} {} 200 Reaper", selected_x, selected_y);
        }
        else {
            // println!("{} {} 0 Reaper", selected_x, selected_y);
            // println!("{} {} 0 Reaper", -my_reaper_speed.vx, -my_reaper_speed.vy);
            println!("WAIT Reaper {} {}", my_reaper_speed.vx, my_reaper_speed.vy);
        }
        
        // Destroyer
        destroyer_decider(
            &my_rage,
            &chosen_tanker,
            my_doof.as_ref(),
            my_destroyer.as_ref(),
            reapers,
            destroyers,
        );

        // Doof
        println!("{} {} 300 Doof", doof_target.x, doof_target.y);
    }
}
