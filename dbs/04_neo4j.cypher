// =====================================================================
// Neo4j - Grafo de recomendación
// Ejecutar con:  cypher-shell -u neo4j -p <pwd> -f dbs/04_neo4j.cypher
// =====================================================================

// 1) Limpieza
MATCH (n) DETACH DELETE n;

// 2) Personas (clientes)
UNWIND [
  {document:'C100', first_name:'Ana',       last_name:'López',    role:'CLIENT', gender:'F', stratum:3, neighborhood:'Cádiz',          municipality:'Ibagué', department:'Tolima'},
  {document:'C101', first_name:'Luis',      last_name:'Martínez', role:'CLIENT', gender:'M', stratum:3, neighborhood:'Cádiz',          municipality:'Ibagué', department:'Tolima'},
  {document:'C102', first_name:'Sofía',     last_name:'Ramírez',  role:'CLIENT', gender:'F', stratum:4, neighborhood:'La Pola',        municipality:'Ibagué', department:'Tolima'},
  {document:'C103', first_name:'Andrés',    last_name:'Torres',   role:'CLIENT', gender:'M', stratum:2, neighborhood:'Jordán',         municipality:'Ibagué', department:'Tolima'},
  {document:'C104', first_name:'Valentina', last_name:'Pérez',    role:'CLIENT', gender:'F', stratum:5, neighborhood:'Piedra Pintada', municipality:'Ibagué', department:'Tolima'}
] AS p
MERGE (per:Person {document: p.document})
SET per += p
MERGE (n:Neighborhood {name: p.neighborhood})
MERGE (m:Municipality {name: p.municipality})
MERGE (d:Department   {name: p.department})
MERGE (g:Gender       {code: p.gender})
MERGE (s:Stratum      {level: p.stratum})
MERGE (per)-[:LIVES_IN]->(n)
MERGE (n)-[:PART_OF]->(m)
MERGE (m)-[:PART_OF]->(d)
MERGE (per)-[:HAS_GENDER]->(g)
MERGE (per)-[:HAS_STRATUM]->(s);

// 3) Productos con sus categorías y tags
UNWIND [
  {sku:'P-001', name:'Laptop Lenovo IdeaPad 3',           price:2500000, brand:'Lenovo',    category:'Electrónica', tags:['portátil','oficina','estudio']},
  {sku:'P-002', name:'Mouse inalámbrico Logitech M170',   price:55000,   brand:'Logitech',  category:'Electrónica', tags:['accesorio','oficina','inalámbrico']},
  {sku:'P-003', name:'Teclado mecánico Redragon Kumara',  price:230000,  brand:'Redragon',  category:'Electrónica', tags:['gaming','accesorio']},
  {sku:'P-004', name:'Monitor LG 24" Full HD',            price:720000,  brand:'LG',        category:'Electrónica', tags:['oficina','estudio']},
  {sku:'P-005', name:'Smartphone Samsung Galaxy A15',     price:850000,  brand:'Samsung',   category:'Electrónica', tags:['móvil','android']},
  {sku:'L-001', name:'Libro: Clean Architecture',         price:120000,  brand:'Pearson',   category:'Libros',      tags:['software','arquitectura','clásico']},
  {sku:'L-002', name:'Libro: Diseño en Patrones',         price:130000,  brand:'Pearson',   category:'Libros',      tags:['software','patrones']},
  {sku:'L-003', name:'Libro: 100 años de soledad',        price:60000,   brand:'Sudamericana', category:'Libros',   tags:['novela','clásico','colombia']},
  {sku:'H-001', name:'Cafetera Oster 12 tazas',           price:180000,  brand:'Oster',     category:'Hogar',       tags:['cocina','desayuno']},
  {sku:'H-002', name:'Licuadora Oster Clásica',           price:250000,  brand:'Oster',     category:'Hogar',       tags:['cocina','clásico']},
  {sku:'R-001', name:'Camiseta Nike Dri-FIT',             price:95000,   brand:'Nike',      category:'Ropa',        tags:['deporte','running']},
  {sku:'R-002', name:'Tenis Adidas Runfalcon',            price:280000,  brand:'Adidas',    category:'Ropa',        tags:['deporte','running','tenis']}
] AS prod
MERGE (p:Product {sku: prod.sku})
SET p.name = prod.name, p.price = prod.price, p.brand = prod.brand
MERGE (c:Category {name: prod.category})
MERGE (p)-[:IN_CATEGORY]->(c)
WITH p, prod
UNWIND prod.tags AS tag
  MERGE (t:Tag {name: tag})
  MERGE (p)-[:HAS_TAG]->(t);

// 4) Compras semilla (vecindad/comportamiento)
UNWIND [
  {doc:'C100', sku:'P-001', qty:1}, {doc:'C100', sku:'P-002', qty:1},
  {doc:'C101', sku:'P-005', qty:1},
  {doc:'C102', sku:'P-004', qty:2}, {doc:'C102', sku:'P-002', qty:1}, {doc:'C102', sku:'L-001', qty:1},
  {doc:'C103', sku:'P-003', qty:1},
  {doc:'C104', sku:'L-001', qty:1}, {doc:'C104', sku:'L-002', qty:1}
] AS r
MATCH (c:Person {document: r.doc}), (p:Product {sku: r.sku})
MERGE (c)-[b:BOUGHT]->(p)
ON CREATE SET b.quantity = r.qty, b.times = 1
ON MATCH  SET b.quantity = b.quantity + r.qty, b.times = b.times + 1;

// 5) Verificación rápida
MATCH (n) RETURN labels(n)[0] AS label, count(*) AS total ORDER BY total DESC;
