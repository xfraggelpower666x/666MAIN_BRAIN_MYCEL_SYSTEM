// Generates src/templates.json: hundreds of profile and gift templates from themes x layouts.
// Every template is checked with the page's own code (build/pure.js): it must parse cleanly and fit
// the game's limits, and gift templates may only use symbols that show in gifts.
//
//   python build.py && node tools/gen-templates.js
"use strict";
const fs = require("fs");
const path = require("path");
const P = require("../build/pure.js");

const ROOT = path.resolve(__dirname, "..");
const SYMBOLS = JSON.parse(fs.readFileSync(path.join(ROOT, "src/symbols.json"), "utf8"));
const PROFILE_ONLY = new Set(SYMBOLS.profileOnly);

// deterministic picks so the file only changes when the generator does
let seed = 7;
const rnd = () => ((seed = (seed * 1103515245 + 12345) % 2147483648) / 2147483648);
const pick = (arr, k) => arr[(k ?? Math.floor(rnd() * 1e9)) % arr.length];
const pickN = (arr, n, k = 0) => Array.from({ length: Math.min(n, arr.length) }, (_, i) => arr[(k + i * 3) % arr.length])
  .filter((v, i, a) => a.indexOf(v) === i);

const c = (col, t) => `<color=${col}>${t}</color>`;
const b = (t) => `<b>${t}</b>`;
const i = (t) => `<i>${t}</i>`;
const sz = (n, t) => `<size=${n}>${t}</size>`;
// gradient across letters (fewer steps = cheaper) using the page's own OKLab blend
function grad(text, stops, mode = "word", steps = 6) {
  const runs = P.gradientRuns([{ t: text, b: false, i: false, c: null, s: null }], 0, [...text].length, stops, mode, steps);
  return P.serialize(runs, { names: true, mergeSpaces: true });
}

// ------------------------------------------------------------------ profile themes
const THEMES = [
  { id: "neon", name: "Neon Nights", cat: "Party & music", col: ["#ff3d8b", "#22d3ee", "#9ca3c9", "#ffd23d"], grad: ["#ff3d8b", "#a855f7", "#22d3ee"],
    deco: ["✦", "✦"], bullet: "▶", div: "▬▬▬▬▬▬▬▬▬▬▬▬", names: ["Nova", "Rio", "Vex"],
    tag: ["night owl · music lover · here for good vibes", "lights low, bass loud, smile on", "always on the dance floor"],
    about: ["I live for late nights, loud music and good company.", "You'll find me where the bass is loudest.", "Say hi, buy me a drink, and let's dance."],
    likes: ["dancing till sunrise", "deep house & techno", "rooftop parties", "neon lights", "meeting new people", "glow sticks"],
    nope: ["drama", "spam in my whispers", "boring small talk", "rude vibes"],
    find: ["Club Pulse on weekends", "the main dance floor", "rooftop at midnight"], want: ["dance partners", "party friends", "good energy"],
    end: ["See you on the floor ✦", "Stay loud, stay kind", "Turn it up!"], quote: ["Dance like nobody's watching.", "The night is young."] },
  { id: "chill", name: "Chill Lounge", cat: "Chill & cozy", col: ["#7dd3fc", "#a7f3d0", "#94a3b8", "#fde68a"], grad: ["#7dd3fc", "#a7f3d0"],
    deco: ["☁", "☁"], bullet: "•", div: "﹏﹏﹏﹏﹏﹏﹏﹏", names: ["Luna", "Kai", "Sol"],
    tag: ["slow mornings · soft music · good talks", "easygoing and always up for a chat", "coffee first, then everything else"],
    about: ["I'm laid-back and love deep conversations.", "Find me in a quiet corner with a good playlist.", "No rush, no stress, just good company."],
    likes: ["lo-fi beats", "sunsets", "long talks", "cozy lounges", "coffee & tea", "rainy days"],
    nope: ["shouting", "rushing", "negativity", "mind games"],
    find: ["the lounge by the fireplace", "chill rooms after midnight", "the quiet beach"], want: ["easy conversation", "new friends", "calm company"],
    end: ["Take it easy ☁", "Peace and good vibes", "Breathe, you're doing great"], quote: ["Slow down and enjoy it.", "Good things take time."] },
  { id: "romance", name: "Sweetheart", cat: "Romance", col: ["#fb7185", "#f9a8d4", "#d4a5b5", "#fecdd3"], grad: ["#e11d48", "#fb7185", "#f9a8d4"],
    deco: ["♥", "♥"], bullet: "♡", div: "♡ ♡ ♡ ♡ ♡ ♡", names: ["Rose", "Amour", "Bella"],
    tag: ["hopeless romantic · candlelight dinners", "looking for my person", "soft heart, big smile"],
    about: ["I believe in sweet gestures and slow dances.", "Romance isn't dead, it just needs a good playlist.", "Kind words go a long way with me."],
    likes: ["slow dances", "love songs", "candlelit dinners", "stargazing", "handwritten notes", "flowers"],
    nope: ["players", "rudeness", "ghosting", "games with feelings"],
    find: ["the rooftop garden", "candlelit cafés", "the beach at sunset"], want: ["someone genuine", "a dance partner", "real connection"],
    end: ["Be sweet, be real ♥", "Love is in the air", "Send a smile my way"], quote: ["All you need is love.", "Every love story is beautiful."] },
  { id: "gamer", name: "Player One", cat: "Gamer", col: ["#4ade80", "#38bdf8", "#94a3b8", "#facc15"], grad: ["#22c55e", "#38bdf8", "#a855f7"],
    deco: ["▶", "◀"], bullet: "►", div: "■■■■■■■■■■", names: ["Pixel", "Byte", "Ace"],
    tag: ["level 99 in good vibes", "AFK? never. GG? always.", "press start to chat"],
    about: ["Gamer by day, dancer by night.", "Ask me about my high score.", "Respawning in the club every evening."],
    likes: ["co-op games", "speedruns", "RGB everything", "retro arcades", "late-night raids", "energy drinks"],
    nope: ["rage quitters", "spoilers", "lag", "toxic chat"],
    find: ["the arcade room", "game night lobby", "online most evenings"], want: ["player two", "squad mates", "friendly rivals"],
    end: ["GG, see you next round", "Player Two? ▶", "Save point reached"], quote: ["It's dangerous to go alone.", "Game on."] },
  { id: "goth", name: "Midnight Goth", cat: "Dark & gothic", col: ["#c084fc", "#ef4444", "#9ca3af", "#e5e7eb"], grad: ["#7e22ce", "#c084fc", "#ef4444"],
    deco: ["✟", "✟"], bullet: "✧", div: "†  †  †  †  †", names: ["Raven", "Morticia", "Vlad"],
    tag: ["dark soul · warm heart", "midnight is my favourite colour", "black lace and old poetry"],
    about: ["I love the dark, the quiet and the mysterious.", "Velvet, candles and a good horror story.", "Don't let the black fool you, I'm friendly."],
    likes: ["gothic music", "old castles", "full moons", "poetry", "candlelight", "rainy nights"],
    nope: ["bright mornings", "shallow talk", "fake people", "loud pop"],
    find: ["the abandoned cathedral", "the cemetery garden", "midnight lounges"], want: ["kindred spirits", "deep talks", "night owls"],
    end: ["Stay mysterious ✟", "The night is ours", "Darkness looks good on you"], quote: ["Not all who wander are lost.", "Embrace the dark."] },
  { id: "pastel", name: "Pastel Dream", cat: "Cute & pastel", col: ["#f9a8d4", "#c4b5fd", "#a5b4cb", "#a5f3fc"], grad: ["#f9a8d4", "#c4b5fd", "#a5f3fc"],
    deco: ["❀", "❀"], bullet: "✿", div: "✿ ❀ ✿ ❀ ✿ ❀ ✿", names: ["Mochi", "Peach", "Bunny"],
    tag: ["soft vibes · sweet treats · big hugs", "sprinkles and sunshine", "cute but chaotic"],
    about: ["I'm calm, kind and a little shy.", "Say hello and I'll make you a drink ♡", "Collector of plushies and good moments."],
    likes: ["bubble tea", "plushies", "pastel everything", "cute outfits", "baking", "kawaii music"],
    nope: ["meanies", "shouting", "messy rooms", "sad endings"],
    find: ["the candy café", "flower gardens", "cozy bedrooms"], want: ["sweet friends", "tea parties", "photo buddies"],
    end: ["Stay sweet ❀", "Sending hugs ♡", "You're adorable"], quote: ["Be the sunshine.", "Stay soft."] },
  { id: "elegant", name: "Velvet Gold", cat: "Elegant", col: ["#fbbf24", "#e5e7eb", "#a8a29e", "#fde68a"], grad: ["#b45309", "#fbbf24", "#fde68a"],
    deco: ["❖", "❖"], bullet: "◆", div: "═══════ ◆ ═══════", names: ["Celeste", "Adrian", "Vivienne"],
    tag: ["classy · calm · curious", "champagne taste, good manners", "elegance is an attitude"],
    about: ["I appreciate fine music, fine company and fine manners.", "Dress code: effortless.", "A gentleman's charm or a lady's grace, always welcome."],
    likes: ["jazz evenings", "art galleries", "fine dining", "classic films", "ballroom dancing", "wine tasting"],
    nope: ["vulgarity", "bad manners", "loud arguments", "rushing"],
    find: ["the grand ballroom", "rooftop bars", "jazz lounges"], want: ["refined company", "a dance partner", "good conversation"],
    end: ["Cheers ❖", "With grace", "Until our next dance"], quote: ["Elegance never fades.", "Less, but better."] },
  { id: "fantasy", name: "Enchanted", cat: "Fantasy", col: ["#a78bfa", "#34d399", "#a5b4c4", "#fde047"], grad: ["#6366f1", "#a78bfa", "#34d399"],
    deco: ["✧", "✧"], bullet: "✦", div: "｡°✩ ｡°✩ ｡°✩ ｡°✩", names: ["Elara", "Faelan", "Lyra"],
    tag: ["half dreamer · half wizard", "lost somewhere in a storybook", "potions brewed daily"],
    about: ["Ask me about dragons, spells and secret forests.", "Every room is better with a little magic.", "I collect stories, crystals and good friends."],
    likes: ["fairy tales", "crystals", "enchanted forests", "dragons", "medieval music", "moonlit walks"],
    nope: ["dull spells", "broken quests", "trolls (the online kind)", "rude goblins"],
    find: ["the hidden forest", "the castle library", "the crystal cave"], want: ["fellow adventurers", "quest companions", "storytellers"],
    end: ["May your path be magical ✧", "Blessed be", "Onward, adventurer"], quote: ["Believe in magic.", "Once upon a time..."] },
  { id: "beach", name: "Beach Days", cat: "Summer", col: ["#38bdf8", "#fbbf24", "#94a3b8", "#fb923c"], grad: ["#0ea5e9", "#38bdf8", "#fbbf24"],
    deco: ["☀", "☀"], bullet: "≈", div: "≈≈≈≈≈≈≈≈≈≈≈≈", names: ["Marina", "Coral", "Bodhi"],
    tag: ["salty hair · sunny heart", "sand between my toes", "forever on summer time"],
    about: ["Happiest by the ocean with a cold drink.", "Sunsets, waves and good playlists.", "Let's go swimming at midnight."],
    likes: ["ocean waves", "beach parties", "surfing", "cocktails", "sunsets", "bonfires"],
    nope: ["cold weather", "bad sunburns", "grumpy people", "rainy beach days"],
    find: ["the beach bar", "the pier at sunset", "pool parties"], want: ["beach buddies", "sunset dates", "summer friends"],
    end: ["Stay salty ☀", "Good vibes only", "See you at the shore"], quote: ["Life's a beach.", "Sun's out, fun's out."] },
  { id: "host", name: "Club Host", cat: "Hosts & DJs", col: ["#f472b6", "#facc15", "#a1a1aa", "#22d3ee"], grad: ["#f472b6", "#facc15"],
    deco: ["★", "★"], bullet: "➳", div: "★ ▬▬▬▬▬▬▬▬ ★", names: ["Diamond", "Monroe", "Sasha"],
    tag: ["your host with the most", "party planner · room owner · DJ", "doors open every Friday"],
    about: ["I run events and love bringing people together.", "Ask about my rooms and parties.", "Everyone's welcome, respect is the dress code."],
    likes: ["hosting events", "themed parties", "new faces", "great music", "dress-up nights", "karaoke"],
    nope: ["trolls", "disrespect", "door crashers", "drama in my rooms"],
    find: ["my club every Friday", "the VIP lounge", "events board"], want: ["party guests", "DJs", "event staff"],
    end: ["Doors open at 9 ★", "Hope to see you there", "Bring a friend!"], quote: ["The party starts with you.", "Good people, good music."] },
  { id: "dj", name: "On the Decks", cat: "Hosts & DJs", col: ["#22d3ee", "#a3e635", "#9ca3af", "#f472b6"], grad: ["#22d3ee", "#a3e635"],
    deco: ["♫", "♫"], bullet: "♪", div: "▀▄▀▄▀▄▀▄▀▄▀▄▀", names: ["DJ Kade", "DJ Echo", "DJ Rhea"],
    tag: ["DJ · producer · bass enthusiast", "spinning beats every weekend", "requests welcome, good vibes required"],
    about: ["I play house, techno and anything that moves the floor.", "Catch my sets live most weekends.", "Music is my love language."],
    likes: ["deep house", "drum & bass", "vinyl", "festival nights", "requests", "new tracks"],
    nope: ["silence", "skipping songs", "talking over drops", "bad speakers"],
    find: ["behind the decks", "Club Pulse on Saturdays", "the radio stream"], want: ["dancers", "music lovers", "collabs"],
    end: ["Turn it up ♫", "See you on the dance floor", "Stay tuned"], quote: ["Music is life.", "Drop the beat."] },
  { id: "minimal", name: "Clean & Simple", cat: "Minimal", col: ["#e5e7eb", "#93c5fd", "#9ca3af", "#fca5a5"], grad: ["#e5e7eb", "#93c5fd"],
    deco: ["·", "·"], bullet: "–", div: "¯¯¯¯¯¯¯¯¯¯¯¯", names: ["Alex", "Sam", "Jordan"],
    tag: ["simple · honest · friendly", "less is more", "just here to chat"],
    about: ["I keep it simple and real.", "Happy to chat about anything.", "Good vibes, no fuss."],
    likes: ["music", "good talks", "travel", "coffee", "films", "friends"],
    nope: ["drama", "spam", "rudeness", "fakes"],
    find: ["around", "most evenings", "the lounge"], want: ["friends", "chats", "good company"],
    end: ["Say hi", "Be kind", "Thanks for stopping by"], quote: ["Keep it simple.", "Be yourself."] },
  { id: "funny", name: "Class Clown", cat: "Funny", col: ["#fde047", "#fb923c", "#a3a3a3", "#4ade80"], grad: ["#fde047", "#fb923c", "#f472b6"],
    deco: ["ツ", "ツ"], bullet: "☺", div: "~ ☺ ~ ☺ ~ ☺ ~", names: ["Giggles", "Chuckles", "Pickle"],
    tag: ["professional overthinker · amateur comedian", "I came for the snacks", "my dance moves are illegal in 3 countries"],
    about: ["Warning: may contain bad jokes.", "I laugh at my own jokes so you don't have to.", "Here for snacks, stayed for the people."],
    likes: ["bad puns", "memes", "snacks", "naps", "dancing badly", "cat videos"],
    nope: ["serious faces", "no snacks", "Mondays", "spoilers"],
    find: ["near the snack table", "on the dance floor (badly)", "in your whispers with memes"], want: ["joke buddies", "snack sharers", "fellow goofballs"],
    end: ["Stay weird ツ", "Smile, it confuses people", "Thanks for reading, here's a cookie"], quote: ["Life's too short to be serious.", "Laughter is free."] },
  { id: "explorer", name: "Wanderer", cat: "Explorer", col: ["#34d399", "#fbbf24", "#a8a29e", "#60a5fa"], grad: ["#059669", "#34d399", "#fbbf24"],
    deco: ["➳", "➳"], bullet: "→", div: "· · · ✈ · · ·", names: ["Atlas", "Juno", "Ezra"],
    tag: ["always on the move", "collecting places, not things", "say hi in any language"],
    about: ["I love exploring new worlds and rooms.", "Show me your favourite hidden spot.", "Every place has a story."],
    likes: ["new places", "photos", "maps", "road trips", "languages", "hidden gems"],
    nope: ["staying still", "closed doors", "boring routes", "bad directions"],
    find: ["somewhere new every night", "the world map", "your favourite room"], want: ["travel buddies", "guides", "new friends"],
    end: ["See you out there ➳", "Adventure awaits", "Bon voyage"], quote: ["Not all who wander are lost.", "Go see the world."] },
  { id: "cosmic", name: "Stardust", cat: "Space", col: ["#818cf8", "#f0abfc", "#a5b4fc", "#fef08a"], grad: ["#312e81", "#818cf8", "#f0abfc"],
    deco: ["☆", "☆"], bullet: "✩", div: "° ☆ ° ☆ ° ☆ °", names: ["Astra", "Orion", "Nebula"],
    tag: ["made of stardust", "head in the stars", "orbiting good vibes"],
    about: ["Ask me about planets, stars and the big questions.", "Late-night stargazer.", "The universe is huge, let's be kind."],
    likes: ["stargazing", "space documentaries", "synthwave", "night skies", "big ideas", "moon phases"],
    nope: ["light pollution", "closed minds", "flat earth talk", "cloudy nights"],
    find: ["the observatory", "the roof under the stars", "space-themed rooms"], want: ["fellow dreamers", "deep thinkers", "night owls"],
    end: ["Reach for the stars ☆", "To infinity", "Shine on"], quote: ["We are all stardust.", "Look up."] },
  { id: "nature", name: "Forest Spirit", cat: "Nature", col: ["#86efac", "#fcd34d", "#a3a3a3", "#7dd3fc"], grad: ["#15803d", "#86efac", "#fcd34d"],
    deco: ["❦", "❦"], bullet: "♣", div: "~ ❦ ~ ❦ ~ ❦ ~", names: ["Willow", "Fern", "Ash"],
    tag: ["tree hugger · flower finder", "happiest in the forest", "grounded and growing"],
    about: ["I love quiet places full of green.", "Nature is my favourite room.", "Let's go for a walk."],
    likes: ["forests", "flowers", "rain", "hiking", "campfires", "birdsong"],
    nope: ["littering", "concrete jungles", "rushing", "noise"],
    find: ["the forest trail", "the garden", "the lakeside"], want: ["walking buddies", "calm friends", "nature lovers"],
    end: ["Stay wild ❦", "Bloom where you're planted", "Breathe in, breathe out"], quote: ["Let it grow.", "Nature heals."] },
  { id: "winter", name: "Snowfall", cat: "Seasons", col: ["#bae6fd", "#e0f2fe", "#94a3b8", "#fca5a5"], grad: ["#38bdf8", "#bae6fd", "#ffffff"],
    deco: ["☃", "☃"], bullet: "✽", div: "✽ ☃ ✽ ☃ ✽ ☃ ✽", names: ["Frost", "Holly", "Noel"],
    tag: ["cocoa · blankets · snow days", "winter is my season", "cold hands, warm heart"],
    about: ["Find me by the fire with hot chocolate.", "I love snowball fights and cozy nights.", "Winter magic all year round."],
    likes: ["snow days", "hot cocoa", "fireplaces", "ice skating", "cozy sweaters", "holiday lights"],
    nope: ["heatwaves", "cold coffee", "wet socks", "grinches"],
    find: ["the ski lodge", "by the fireplace", "the ice rink"], want: ["cozy company", "snowball partners", "skating buddies"],
    end: ["Stay warm ☃", "Let it snow", "Hugs and hot cocoa"], quote: ["Let it snow.", "Winter is coming."] },
  { id: "spooky", name: "Spooky Season", cat: "Seasons", col: ["#fb923c", "#a855f7", "#a3a3a3", "#4ade80"], grad: ["#ea580c", "#fb923c", "#a855f7"],
    deco: ["☠", "☠"], bullet: "✟", div: "☠ ✟ ☠ ✟ ☠ ✟ ☠", names: ["Hex", "Pumpkin", "Wednesday"],
    tag: ["spooky all year round", "witch please", "boo! did I scare you?"],
    about: ["Halloween is my favourite holiday.", "Haunted houses and horror movies, yes please.", "I'm sweet, mostly."],
    likes: ["horror movies", "haunted houses", "pumpkins", "costumes", "candy", "ghost stories"],
    nope: ["jump scares (okay, maybe)", "no candy", "lame costumes", "daylight"],
    find: ["the haunted mansion", "the graveyard party", "pumpkin patches"], want: ["fellow ghouls", "costume buddies", "horror fans"],
    end: ["Stay spooky ☠", "Trick or treat", "Boo!"], quote: ["Something wicked this way comes.", "Boo."] },
  { id: "story", name: "Storyteller", cat: "Roleplay", col: ["#fcd34d", "#f87171", "#a8a29e", "#93c5fd"], grad: ["#b45309", "#fcd34d"],
    deco: ["『", "』"], bullet: "✎", div: "═══ ✎ ═══", names: ["Scribe", "Bard", "Sage"],
    tag: ["roleplayer · writer · dreamer", "every room is a story", "in character, mostly"],
    about: ["I love building stories with other people.", "Ask me for a scene and I'll set the stage.", "Plot twists are my favourite."],
    likes: ["roleplay", "plot twists", "world-building", "character arcs", "fantasy & sci-fi", "good writing"],
    nope: ["godmodding", "one-word replies", "meta gaming", "breaking scenes"],
    find: ["the tavern", "the library", "story rooms"], want: ["writing partners", "story arcs", "creative friends"],
    end: ["The story continues...", "Write with me ✎", "To be continued"], quote: ["Every story matters.", "Once upon a time..."] },
  { id: "taken", name: "Taken & Happy", cat: "Romance", col: ["#f43f5e", "#fda4af", "#d4a5b5", "#fde68a"], grad: ["#be123c", "#f43f5e", "#fda4af"],
    deco: ["❤", "❤"], bullet: "♥", div: "❤ ═════════ ❤", names: ["Mia & Leo", "Ivy & Max", "Ella & Noah"],
    tag: ["happily taken · still friendly", "two hearts, one beat", "partners in crime"],
    about: ["We love dancing together and meeting new friends.", "Here as a couple, happy to chat.", "Respect our relationship and we'll get along great."],
    likes: ["date nights", "slow dances", "couple outfits", "double dates", "music", "friends"],
    nope: ["flirting with my partner", "drama", "jealousy games", "rude whispers"],
    find: ["the ballroom together", "romantic rooms", "the beach at sunset"], want: ["couple friends", "fun nights", "good company"],
    end: ["Love wins ❤", "Together is better", "Be kind, be happy"], quote: ["Better together.", "Love is all you need."] },
];

// layouts: (theme, k) -> code. k varies wording between templates of the same theme.
const H = (t, txt) => b(c(t.col[1], txt));
const PROFILE_LAYOUTS = [
  { name: "Spotlight", make: (t, k) => {
    const n = pick(t.names, k);
    return [sz(26, b(c(t.col[0], `${t.deco[0]} Hey, I'm ${n} ${t.deco[1]}`))), c(t.col[2], pick(t.tag, k)), "",
      H(t, `${t.bullet} I'm into`), ...pickN(t.likes, 3, k).map((x) => `${c(t.col[1], t.bullet)} ${x}`), "",
      H(t, `${t.bullet} Not for me`), ...pickN(t.nope, 2, k).map((x) => `${c(t.col[3], t.bullet)} ${x}`), "",
      sz(12, c(t.col[2], pick(t.end, k)))].join("\n"); } },
  { name: "Gradient title", make: (t, k) => {
    const n = pick(t.names, k + 1);
    return [sz(30, b(grad(n.toUpperCase(), t.grad, "letter", Math.min(8, [...n].length)))), c(t.col[2], t.div), "",
      pick(t.about, k), pick(t.about, k + 1), "",
      c(t.col[1], pickN(t.likes, 4, k).join(" · ")), "",
      sz(12, i(c(t.col[2], pick(t.end, k + 1))))].join("\n"); } },
  { name: "Do's and don'ts", make: (t, k) => {
    const n = pick(t.names, k + 2);
    return [sz(22, b(c(t.col[0], `${t.deco[0]} ${n} ${t.deco[1]}`))), pick(t.about, k + 2), "",
      b(c("#59ff00", "My do's")), ...pickN(["Say hi first", "Ask me to dance", "Send good vibes", "Share your favourite song", "Invite me to events"], 3, k).map((x) => `${c("#59ff00", " ▶")} ${x}`), "",
      b(c("red", "My don'ts")), ...pickN(t.nope, 3, k).map((x) => `${c("red", " ▶")} ${x[0].toUpperCase() + x.slice(1)}`), "",
      sz(12, c(t.col[2], pick(t.end, k + 2)))].join("\n"); } },
  { name: "Status board", make: (t, k) => {
    const n = pick(t.names, k);
    return [sz(16, b("( ) Online   (✓) AFK   ( ) Busy")), "",
      sz(22, c(t.col[0], `${t.deco[0]} ${n} ${t.deco[1]}`)), c(t.col[2], pick(t.tag, k + 1)), "",
      H(t, "Find me"), ...pickN(t.find, 2, k).map((x) => `${t.bullet} ${c(t.col[1], x)}`), "",
      H(t, "Looking for"), ...pickN(t.want, 2, k).map((x) => `${t.bullet} ${x}`)].join("\n"); } },
  { name: "Q&A card", make: (t, k) => {
    const f = (label, v) => `${b(c(t.col[1], label + ":"))} ${v}`;
    return [sz(24, b(c(t.col[0], `${t.deco[0]} ${pick(t.names, k + 1)}`))), c(t.col[2], t.div),
      f("Vibe", pick(t.tag, k + 2)), f("Into", pickN(t.likes, 3, k + 1).join(", ")), f("Find me", pick(t.find, k)),
      f("Looking for", pick(t.want, k + 1)), f("Not into", pickN(t.nope, 2, k + 1).join(", ")), c(t.col[2], t.div),
      sz(12, c(t.col[3], pick(t.end, k)))].join("\n"); } },
  { name: "House rules", make: (t, k) => {
    const nums = ["①", "②", "③", "④"];
    const rules = ["Be kind, always", `No ${pick(t.nope, k)}`, "Ask before you whisper", "Have fun and dance", "Respect my space", "Good vibes only"];
    return [sz(24, b(c(t.col[0], `${t.deco[0]} ${pick(t.names, k)}'s rules ${t.deco[1]}`))), "",
      ...pickN(rules, 4, k).map((x, j) => `${c(t.col[1], nums[j])} ${x}`), "",
      c(t.col[2], pick(t.about, k)), sz(12, c(t.col[3], pick(t.end, k + 2)))].join("\n"); } },
  { name: "Big quote", make: (t, k) => [
    sz(28, i(c(t.col[0], `“${pick(t.quote, k)}”`))), "", sz(20, b(c(t.col[1], pick(t.names, k + 2)))), c(t.col[2], pick(t.tag, k)), "",
    pick(t.about, k + 1), "", `${c(t.col[3], t.bullet)} ${pickN(t.likes, 3, k + 2).join(` ${c(t.col[3], t.bullet)} `)}`].join("\n") },
  { name: "Minimal", make: (t, k) => [
    sz(26, b(pick(t.names, k))), c(t.col[2], pick(t.tag, k + 2)), "",
    pick(t.about, k), "", c(t.col[1], pickN(t.likes, 3, k + 3).join("  ·  "))].join("\n") },
  { name: "Banner", make: (t, k) => [
    c(t.col[1], t.div), sz(26, b(grad(`${t.deco[0]} ${pick(t.names, k + 1)} ${t.deco[1]}`, t.grad, "word"))), c(t.col[1], t.div), "",
    `${b(c(t.col[0], "About me"))}`, pick(t.about, k), pick(t.about, k + 2), "",
    `${b(c(t.col[0], "Looking for"))}`, pickN(t.want, 2, k).join(" & "), "",
    sz(12, c(t.col[2], pick(t.end, k)))].join("\n") },
];

// ------------------------------------------------------------------ gift occasions
const OCCASIONS = [
  { id: "bday", name: "Birthday", cat: "Birthday", col: ["#f472b6", "#fbbf24", "#22d3ee"], sym: "★", title: ["Happy Birthday", "Happy B-day", "It's your day"],
    msg: ["Have the best day ever!", "Make a wish and dance all night!", "Another year more awesome!", "Cake, music and you. Perfect."] },
  { id: "love", name: "Love", cat: "Love", col: ["red", "#fb7185", "#f9a8d4"], sym: "♥", title: ["For you", "My love", "Always yours"],
    msg: ["You make my heart dance.", "Every moment with you is magic.", "I'm so lucky to have you.", "You're my favourite person."] },
  { id: "thanks", name: "Thank you", cat: "Thank you", col: ["#4ade80", "#fde047", "#7dd3fc"], sym: "✿", title: ["Thank you", "Thanks so much", "Grateful for you"],
    msg: ["You're the best, really.", "That meant a lot to me.", "Thanks for being amazing.", "I owe you a dance!"] },
  { id: "friend", name: "Friendship", cat: "Friendship", col: ["#38bdf8", "#facc15", "#f472b6"], sym: "ツ", title: ["Best friends", "Bestie", "To my friend"],
    msg: ["Friends forever, no matter what.", "Thanks for always being there.", "You make every room better.", "Partner in crime for life!"] },
  { id: "congrats", name: "Congratulations", cat: "Congrats", col: ["#fbbf24", "#a855f7", "#22d3ee"], sym: "★", title: ["Congrats", "Well done", "You did it"],
    msg: ["So proud of you!", "You earned this!", "Big win, bigger party!", "Cheers to you!"] },
  { id: "welcome", name: "Welcome", cat: "Welcome", col: ["#22d3ee", "#4ade80", "#fde047"], sym: "▶", title: ["Welcome", "Welcome in", "Hello there"],
    msg: ["So glad you're here!", "Make yourself at home.", "Welcome to the family!", "Let the fun begin!"] },
  { id: "sorry", name: "Sorry", cat: "Sorry", col: ["#93c5fd", "#c4b5fd", "#f9a8d4"], sym: "♡", title: ["I'm sorry", "Forgive me?", "My bad"],
    msg: ["I didn't mean it. Friends again?", "Can we start over?", "You matter to me.", "Hug it out?"] },
  { id: "night", name: "Good night", cat: "Good night", col: ["#818cf8", "#fde68a", "#c4b5fd"], sym: "☆", title: ["Good night", "Sweet dreams", "Nighty night"],
    msg: ["Sleep tight, see you tomorrow.", "Dream of something wonderful.", "Rest well, superstar.", "The stars say good night too."] },
  { id: "party", name: "Party", cat: "Party", col: ["#ff3d8b", "#22d3ee", "#fde047"], sym: "♫", title: ["Party time", "Let's dance", "Turn it up"],
    msg: ["See you on the dance floor!", "Tonight we celebrate!", "Drinks are on me!", "Bring your best moves!"] },
  { id: "xmas", name: "Christmas", cat: "Holidays", col: ["red", "#22c55e", "#fde047"], sym: "☃", title: ["Merry Christmas", "Happy holidays", "Season's greetings"],
    msg: ["Warm wishes and cozy nights!", "Hope Santa spoils you!", "Joy, peace and hot cocoa!", "Have a magical holiday!"] },
  { id: "newyear", name: "New Year", cat: "Holidays", col: ["#fbbf24", "#e5e7eb", "#a855f7"], sym: "☆", title: ["Happy New Year", "Cheers to the new year", "New year, new vibes"],
    msg: ["Here's to an amazing year!", "Let's make it the best one yet!", "Cheers to us!", "New adventures await!"] },
  { id: "valentine", name: "Valentine's Day", cat: "Holidays", col: ["red", "#f472b6", "#fecdd3"], sym: "♥", title: ["Be my Valentine", "Happy Valentine's", "Love you"],
    msg: ["You stole my heart.", "Roses are red, you're amazing.", "My heart beats for you.", "Will you be mine?"] },
  { id: "halloween", name: "Halloween", cat: "Holidays", col: ["#fb923c", "#a855f7", "#4ade80"], sym: "♠", title: ["Happy Halloween", "Trick or treat", "Boo"],
    msg: ["Hope you get all the candy!", "Have a spooky night!", "You're my favourite ghoul!", "Stay creepy!"] },
  { id: "getwell", name: "Get well", cat: "Get well", col: ["#4ade80", "#7dd3fc", "#fde047"], sym: "✚", title: ["Get well soon", "Feel better", "Healing hugs"],
    msg: ["Sending you hugs and soup!", "Rest up, we miss you!", "Get better fast!", "Thinking of you."] },
  { id: "miss", name: "Miss you", cat: "Friendship", col: ["#c4b5fd", "#f9a8d4", "#93c5fd"], sym: "☁", title: ["Miss you", "Thinking of you", "Come back soon"],
    msg: ["It's not the same without you.", "Can't wait to see you again!", "The dance floor misses you.", "Come back soon!"] },
  { id: "cheers", name: "Cheers", cat: "Party", col: ["#fbbf24", "#f472b6", "#22d3ee"], sym: "♪", title: ["Cheers", "To you", "Bottoms up"],
    msg: ["Here's to good times!", "Drinks and good vibes!", "To friends and music!", "Raise your glass!"] },
];

const GIFT_LAYOUTS = [
  { name: "Big line", make: (o, k) => sz(38, `${c(o.col[0], o.sym)} ${pick(o.title, k)} %username% ${c(o.col[0], o.sym)}`) },
  { name: "Title + message", make: (o, k) => [sz(30, b(c(o.col[0], `${pick(o.title, k)}, %username%!`))), c(o.col[1], pick(o.msg, k))].join("\n") },
  { name: "Gradient", make: (o, k) => [sz(32, b(grad(pick(o.title, k + 1), [o.col[0], o.col[2]], "word"))), `%username%, ${pick(o.msg, k + 1).toLowerCase()}`].join("\n") },
  { name: "Framed", make: (o, k) => [c(o.col[1], `${o.sym} ${o.sym} ${o.sym}`), sz(28, b(pick(o.title, k + 2))), `For %username%`, c(o.col[1], `${o.sym} ${o.sym} ${o.sym}`)].join("\n") },
  { name: "Note", make: (o, k) => [`${b(c(o.col[0], "To:"))} %username%`, i(pick(o.msg, k + 2)), sz(24, c(o.col[1], `${o.sym} ${pick(o.title, k)} ${o.sym}`))].join("\n") },
  { name: "Two-tone", make: (o, k) => sz(34, `${b(c(o.col[0], pick(o.title, k + 1)))}\n${c(o.col[2], "%username%")}`) },
  { name: "Sparkle", make: (o, k) => [sz(26, `${c(o.col[2], o.sym)} ${b(c(o.col[0], pick(o.title, k)))} ${c(o.col[2], o.sym)}`), `${pick(o.msg, k + 3)}`, sz(14, c(o.col[1], "from your friend ♥"))].join("\n") },
  { name: "Simple", make: (o, k) => `${pick(o.title, k + 2)}, %username%! ${c(o.col[0], o.sym)}\n${c(o.col[1], pick(o.msg, k))}` },
];

// ------------------------------------------------------------------ build + validate
// Symbols known to display in the game: everything in symbols.json (gifts: only the "common" set)
const KNOWN = new Set([...SYMBOLS.common, ...SYMBOLS.profileOnly].flatMap((x) => [...x]));
const GIFT_OK = new Set(SYMBOLS.common.flatMap((x) => [...x]));
const isSymbol = (ch) => ch.codePointAt(0) >= 0x2010 && !/[‘’“”…–—]/.test(ch);

function check(mode, code) {
  const p = P.parseCode(code);
  const text = p.runs.map((r) => r.t).join("");
  const unknown = [...new Set([...text].filter((ch) => isSymbol(ch) && !(mode === "gift" ? GIFT_OK : KNOWN).has(ch)))];
  if (unknown.length) return `${mode === "gift" ? "not gift-safe" : "unknown"} symbols: ${unknown.join(" ")}`;
  if (p.warnings.length) return `parse warnings: ${p.warnings.join("; ")}`;
  const out = P.serialize(p.runs, { names: true, mergeSpaces: true });
  const chars = P.charCount(out);
  if (mode === "profile" && chars > 1000) return `${chars} chars`;
  if (mode === "gift") {
    if (chars > 240) return `${chars} chars`;
    const bytes = P.byteCount(out);
    if (bytes > 255) return `${bytes} bytes`;
    const bad = [...out].filter((ch) => PROFILE_ONLY.has(ch));
    if (bad.length) return `profile-only symbols: ${[...new Set(bad)].join(" ")}`;
  }
  return null;
}

const result = { profile: [], gift: [] };
const problems = [];
THEMES.forEach((t, ti) => PROFILE_LAYOUTS.forEach((L, li) => {
  const code = L.make(t, ti + li);
  const err = check("profile", code);
  if (err) problems.push(`profile ${t.name} / ${L.name}: ${err}`);
  else result.profile.push({ name: `${t.name} · ${L.name}`, cat: t.cat, code: P.serialize(P.parseCode(code).runs, { names: true, mergeSpaces: true }) });
}));
OCCASIONS.forEach((o, oi) => GIFT_LAYOUTS.forEach((L, li) => {
  const code = L.make(o, oi + li);
  const err = check("gift", code);
  if (err) problems.push(`gift ${o.name} / ${L.name}: ${err}`);
  else result.gift.push({ name: `${o.name} · ${L.name}`, cat: o.cat, code: P.serialize(P.parseCode(code).runs, { names: true, mergeSpaces: true }) });
}));

fs.writeFileSync(path.join(ROOT, "src/templates.json"), JSON.stringify(result, null, 0).replace(/\},\{/g, "},\n{") + "\n");
console.log(`profile templates: ${result.profile.length}, gift templates: ${result.gift.length}, skipped: ${problems.length}`);
problems.forEach((p) => console.log("  skipped " + p));
