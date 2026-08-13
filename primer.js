/* Build the teaching graph from examples/smith-preterm.ttl */
(function () {
  const EVI = "https://w3id.org/EVI#";
  const SCHEMA = "http://schema.org/";
  const DCT = "http://purl.org/dc/terms/";
  const RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#";
  const PROV_PERSON = "http://www.w3.org/ns/prov#Person";

  const TYPES = {
    [PROV_PERSON]: { kind: "Person", color: "#6b4f2a" },
    [EVI + "Dataset"]: { kind: "Dataset", color: "#2a5f7a" },
    [EVI + "Schema"]: { kind: "Schema", color: "#4a6b7a" },
    [EVI + "Software"]: { kind: "Software", color: "#3d6b4f" },
    [EVI + "Computation"]: { kind: "Computation", color: "#7a4a2a" },
  };

  const EDGES = {
    [EVI + "createdBy"]: "createdBy",
    [EVI + "associatedWith"]: "associatedWith",
    [EVI + "usedDataset"]: "usedDataset",
    [EVI + "usedSoftware"]: "usedSoftware",
    [EVI + "generated"]: "generated",
    [EVI + "hasSchema"]: "hasSchema",
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

  async function main() {
    const detail = document.getElementById("detail");
    const res = await fetch("examples/smith-preterm.ttl");
    if (!res.ok) {
      detail.textContent = "Could not load examples/smith-preterm.ttl";
      return;
    }
    const ttl = await res.text();
    const quads = new N3.Parser().parse(ttl);

    const bySubject = new Map();
    for (const q of quads) {
      const s = q.subject.id || q.subject.value;
      if (!bySubject.has(s)) bySubject.set(s, []);
      bySubject.get(s).push(q);
    }

    const nodes = [];
    const triples = {};
    for (const [s, qs] of bySubject) {
      let meta = null;
      let label = localName(s);
      for (const q of qs) {
        const p = q.predicate.id || q.predicate.value;
        const o = q.object.id || q.object.value;
        if (p === RDF + "type" && TYPES[o]) meta = TYPES[o];
        if (p === SCHEMA + "name" || p === DCT + "title") label = literal(q.object);
        if (p === EVI + "state") label = literal(q.object);
      }
      triples[s] = qs.map((q) => {
        const p = localName(q.predicate.id || q.predicate.value);
        const o = q.object.termType === "Literal"
          ? JSON.stringify(literal(q.object))
          : localName(q.object.id || q.object.value);
        return localName(s) + "  " + p + "  " + o;
      });
      if (!meta) continue;
      nodes.push({
        id: s,
        label: label + "\n(" + meta.kind + ")",
        color: meta.color,
        font: { color: "#fff", size: 14, face: "system-ui" },
        shape: "box",
        margin: 12,
      });
    }

    const nodeIds = new Set(nodes.map((n) => n.id));
    const edges = [];
    for (const q of quads) {
      const p = q.predicate.id || q.predicate.value;
      const label = EDGES[p];
      if (!label) continue;
      const s = q.subject.id || q.subject.value;
      const o = q.object.id || q.object.value;
      if (!nodeIds.has(s) || !nodeIds.has(o)) continue;
      edges.push({
        from: s,
        to: o,
        label: label,
        arrows: "to",
        color: { color: "#1f3b5b" },
        font: { align: "middle", size: 12, face: "system-ui" },
      });
    }

    const net = new vis.Network(
      document.getElementById("graph"),
      { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) },
      {
        physics: { barnesHut: { gravitationalConstant: -12000, springLength: 180 } },
        edges: { smooth: { type: "cubicBezier" } },
        interaction: { hover: true },
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
