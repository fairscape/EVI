/* Build the teaching graph from examples/smith-preterm.ttl */
(function () {
  const EVI = "https://w3id.org/EVI#";
  const SCHEMA = "http://schema.org/";
  const DCT = "http://purl.org/dc/terms/";
  const RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
  const PROV_PERSON = "http://www.w3.org/ns/prov#Person";

  const TYPES = {
    [PROV_PERSON]: { kind: "Person", color: "#c45c26", level: 0 },
    [EVI + "Dataset"]: { kind: "Dataset", color: "#0f5c6b", level: 1 },
    [EVI + "Schema"]: { kind: "Schema", color: "#3d6b4f", level: 2 },
    [EVI + "Software"]: { kind: "Software", color: "#355f8a", level: 1 },
    [EVI + "Computation"]: { kind: "Computation", color: "#6b3d5c", level: 3 },
  };

  // Display direction: story reads left-to-right (agent → data/software → run → result).
  const EDGES = {
    [EVI + "createdBy"]: { label: "created", reverse: true },
    [EVI + "associatedWith"]: { label: "ran", reverse: true },
    [EVI + "usedDataset"]: { label: "used dataset" },
    [EVI + "usedSoftware"]: { label: "used software" },
    [EVI + "generated"]: { label: "generated" },
    [EVI + "hasSchema"]: { label: "has schema" },
  };

  function localName(iri) {
    const s = String(iri);
    const hash = s.lastIndexOf("#");
    if (hash >= 0) return s.slice(hash + 1);
    return s.slice(s.lastIndexOf("/") + 1);
  }

  function literal(value) {
    if (value && typeof value === "object" && "value" in value) return value.value;
    return String(value);
  }

  function iri(term) {
    return term.id || term.value;
  }

  async function main() {
    const detail = document.getElementById("detail");
    const legend = document.getElementById("legend");
    const res = await fetch("examples/smith-preterm.ttl");
    if (!res.ok) {
      detail.textContent = "Could not load examples/smith-preterm.ttl";
      return;
    }
    const ttl = await res.text();
    const quads = new N3.Parser().parse(ttl);

    const bySubject = new Map();
    for (const q of quads) {
      const s = iri(q.subject);
      if (!bySubject.has(s)) bySubject.set(s, []);
      bySubject.get(s).push(q);
    }

    const seenKinds = [];
    const nodes = [];
    const triples = {};
    const typeOf = {};
    for (const [s, qs] of bySubject) {
      let meta = null;
      let label = localName(s);
      for (const q of qs) {
        const p = iri(q.predicate);
        const o = iri(q.object);
        if (p === RDF + "type" && TYPES[o]) meta = TYPES[o];
        if (p === SCHEMA + "name" || p === DCT + "title") label = literal(q.object);
      }
      triples[s] = qs.map((q) => {
        const p = localName(iri(q.predicate));
        const o = q.object.termType === "Literal"
          ? JSON.stringify(literal(q.object))
          : localName(iri(q.object));
        return localName(s) + "  " + p + "  " + o;
      });
      if (!meta) continue;
      typeOf[s] = meta.kind;
      if (!seenKinds.some((k) => k.kind === meta.kind)) seenKinds.push(meta);
      const level = meta.kind === "Dataset" && /corr|result/i.test(label) ? 4 : meta.level;
      nodes.push({
        id: s,
        label: label + "\n" + meta.kind,
        color: { background: meta.color, border: meta.color, highlight: { background: "#14202b", border: "#c45c26" } },
        font: { color: "#fff", size: 13, face: "system-ui", multi: true },
        shape: "box",
        margin: 14,
        level: level,
      });
    }

    if (legend) {
      legend.innerHTML = seenKinds.map((m) =>
        "<li><span class=\"swatch\" style=\"background:" + m.color + "\"></span>" + m.kind + "</li>"
      ).join("");
    }

    const nodeIds = new Set(nodes.map((n) => n.id));
    const edges = [];
    for (const q of quads) {
      const spec = EDGES[iri(q.predicate)];
      if (!spec) continue;
      let s = iri(q.subject);
      let o = iri(q.object);
      if (spec.reverse) {
        const tmp = s; s = o; o = tmp;
      }
      if (!nodeIds.has(s) || !nodeIds.has(o)) continue;
      edges.push({
        from: s,
        to: o,
        label: spec.label,
        arrows: "to",
        color: { color: "#5b6570", highlight: "#c45c26" },
        font: { align: "middle", size: 11, face: "system-ui", color: "#5b6570" },
        width: 1.4,
      });
    }

    const net = new vis.Network(
      document.getElementById("graph"),
      { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) },
      {
        layout: {
          hierarchical: {
            enabled: true,
            direction: "LR",
            sortMethod: "directed",
            levelSeparation: 170,
            nodeSpacing: 90,
            treeSpacing: 80,
          },
        },
        physics: false,
        edges: { smooth: { type: "cubicBezier", forceDirection: "horizontal", roundness: 0.4 } },
        interaction: { hover: true, dragNodes: true },
      }
    );
    net.on("click", (params) => {
      if (!params.nodes.length) return;
      detail.textContent = (triples[params.nodes[0]] || []).join("\n");
    });
  }

  main().catch((err) => {
    document.getElementById("detail").textContent = String(err);
  });
})();
