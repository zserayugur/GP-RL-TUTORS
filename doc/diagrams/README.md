# Diagrams

All diagrams are written as PlantUML text files (`.puml`) so anyone can edit them; the `.png` files are generated from them.

- `style.iuml` — shared style for every diagram.
- `use-case/` — use case diagrams, one per actor (advisor request: a detailed diagram per actor with its related use cases).

## Regenerating the images

PlantUML needs Java. Download `plantuml.jar` from https://github.com/plantuml/plantuml/releases (not stored in this repo), then run from this folder:

```bash
java -jar /path/to/plantuml.jar -tpng use-case/*.puml
```

The diagrams use PlantUML's built-in layout (`!pragma layout smetana`), so Graphviz is not needed.
