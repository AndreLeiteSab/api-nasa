// Fonte única de verdade que descreve cada endpoint do gateway que a UI pode
// chamar. Cada serviço agrupa um ou mais endpoints; cada endpoint declara seu
// template de caminho, os fields (renderizados como formulário) e uma flag
// opcional `binary`.
//
// A ordem segue os 16 serviços exigidos no trabalho.

export const CATALOG = [
  {
    id: 'apod',
    name: 'APOD',
    description: 'Astronomy Picture of the Day — a imagem astronômica do dia.',
    endpoints: [
      {
        id: 'apod-get',
        label: 'Imagem do dia',
        path: '/apod',
        fields: [
          { name: 'date', label: 'Data (YYYY-MM-DD)', type: 'date' },
          { name: 'start_date', label: 'Início', type: 'date' },
          { name: 'end_date', label: 'Fim', type: 'date' },
          { name: 'count', label: 'Qtd. aleatória', type: 'number' },
        ],
      },
    ],
  },
  {
    id: 'neows',
    name: 'NeoWs (Asteroides)',
    description: 'Objetos próximos da Terra (Near Earth Objects).',
    endpoints: [
      {
        id: 'neows-feed',
        label: 'Feed por datas',
        path: '/neows/feed',
        fields: [
          { name: 'start_date', label: 'Início', type: 'date' },
          { name: 'end_date', label: 'Fim (máx. +7 dias)', type: 'date' },
        ],
      },
      {
        id: 'neows-browse',
        label: 'Navegar (paginado)',
        path: '/neows/browse',
        fields: [
          { name: 'page', label: 'Página', type: 'number' },
          { name: 'size', label: 'Tamanho', type: 'number' },
        ],
      },
      {
        id: 'neows-lookup',
        label: 'Buscar por ID',
        path: '/neows/{asteroid_id}',
        fields: [{ name: 'asteroid_id', label: 'ID do asteroide', type: 'text', required: true }],
      },
    ],
  },
  {
    id: 'donki',
    name: 'DONKI (Clima Espacial)',
    description: 'Notificações e eventos de clima espacial.',
    endpoints: [
      donkiDated('cme', 'Coronal Mass Ejection'),
      donkiDated('gst', 'Tempestade Geomagnética'),
      donkiDated('flr', 'Erupção Solar (FLR)'),
      donkiDated('sep', 'Partículas Energéticas (SEP)'),
      donkiDated('ips', 'Choque Interplanetário'),
      donkiDated('mpc', 'Magnetopause Crossing'),
      donkiDated('rbe', 'Radiation Belt Enhancement'),
      donkiDated('hss', 'High Speed Stream'),
      donkiDated('wsa-enlil', 'WSA+Enlil'),
      donkiDated('cme-analysis', 'CME Analysis'),
      {
        id: 'donki-notifications',
        label: 'Notificações',
        path: '/donki/notifications',
        fields: [
          { name: 'start_date', label: 'Início', type: 'date' },
          { name: 'end_date', label: 'Fim', type: 'date' },
          { name: 'type', label: 'Tipo (all, FLR, CME...)', type: 'text' },
        ],
      },
    ],
  },
  {
    id: 'eonet',
    name: 'EONET',
    description: 'Eventos naturais da Terra (incêndios, tempestades...).',
    endpoints: [
      {
        id: 'eonet-events',
        label: 'Eventos',
        path: '/eonet/events',
        fields: [
          { name: 'status', label: 'Status (open/closed)', type: 'text' },
          { name: 'limit', label: 'Limite', type: 'number' },
          { name: 'days', label: 'Últimos N dias', type: 'number' },
          { name: 'category', label: 'Categoria', type: 'text' },
        ],
      },
      { id: 'eonet-categories', label: 'Categorias', path: '/eonet/categories', fields: [] },
      { id: 'eonet-sources', label: 'Fontes', path: '/eonet/sources', fields: [] },
      { id: 'eonet-layers', label: 'Camadas', path: '/eonet/layers', fields: [] },
      { id: 'eonet-magnitudes', label: 'Magnitudes', path: '/eonet/magnitudes', fields: [] },
    ],
  },
  {
    id: 'epic',
    name: 'EPIC',
    description: 'Imagens da Terra inteira (câmera DSCOVR/EPIC).',
    endpoints: [
      {
        id: 'epic-latest',
        label: 'Mais recentes',
        path: '/epic/{collection}',
        fields: [{ name: 'collection', label: 'Coleção (natural/enhanced)', type: 'text', required: true, default: 'natural' }],
      },
      {
        id: 'epic-date',
        label: 'Por data',
        path: '/epic/{collection}/date/{date}',
        fields: [
          { name: 'collection', label: 'Coleção', type: 'text', required: true, default: 'natural' },
          { name: 'date', label: 'Data (YYYY-MM-DD)', type: 'date', required: true },
        ],
      },
      {
        id: 'epic-available',
        label: 'Datas disponíveis',
        path: '/epic/{collection}/available',
        fields: [{ name: 'collection', label: 'Coleção', type: 'text', required: true, default: 'natural' }],
      },
    ],
  },
  {
    id: 'exoplanet',
    name: 'Exoplanet Archive',
    description: 'Consulta ao arquivo de exoplanetas (TAP/ADQL).',
    endpoints: [
      {
        id: 'exo-query',
        label: 'Consultar',
        path: '/exoplanet',
        fields: [
          { name: 'table', label: 'Tabela (ps, pscomppars)', type: 'text', default: 'ps' },
          { name: 'select', label: 'Colunas (ex.: pl_name,hostname,disc_year)', type: 'text' },
          { name: 'where', label: 'Filtro WHERE (ex.: disc_year>2020)', type: 'text' },
          { name: 'order', label: 'Ordenação (ex.: disc_year desc)', type: 'text' },
          { name: 'limit', label: 'Máx. de linhas', type: 'number', default: 100 },
        ],
      },
    ],
  },
  {
    id: 'gibs',
    name: 'GIBS (Satélite WMTS)',
    description: 'Imagens globais de satélite servidas em tiles (WMTS).',
    endpoints: [
      { id: 'gibs-layers', label: 'Camadas (exemplos)', path: '/gibs/layers', fields: [] },
      {
        id: 'gibs-tile',
        label: 'Tile (imagem)',
        path: '/gibs/tile/{tile_matrix}/{tile_row}/{tile_col}',
        binary: true,
        fields: [
          { name: 'tile_matrix', label: 'Zoom (TileMatrix)', type: 'number', required: true, default: 2 },
          { name: 'tile_row', label: 'Linha (TileRow)', type: 'number', required: true, default: 1 },
          { name: 'tile_col', label: 'Coluna (TileCol)', type: 'number', required: true, default: 2 },
          { name: 'layer', label: 'Camada', type: 'text', default: 'MODIS_Terra_CorrectedReflectance_TrueColor' },
          { name: 'date', label: 'Data', type: 'date' },
          { name: 'tile_matrix_set', label: 'Matrix set', type: 'text', default: '250m' },
        ],
      },
      {
        id: 'gibs-caps',
        label: 'Catálogo WMTS (XML)',
        path: '/gibs/capabilities',
        fields: [{ name: 'epsg', label: 'Projeção', type: 'text', default: 'epsg4326' }],
      },
    ],
  },
  {
    id: 'insight',
    name: 'InSight (Marte)',
    description: 'Clima em Marte (missão InSight — dados podem estar vazios).',
    endpoints: [{ id: 'insight-weather', label: 'Clima', path: '/insight', fields: [] }],
  },
  {
    id: 'images',
    name: 'Image & Video Library',
    description: 'Biblioteca de mídia da NASA.',
    endpoints: [
      {
        id: 'images-search',
        label: 'Buscar',
        path: '/images/search',
        fields: [
          { name: 'q', label: 'Termo', type: 'text', required: true, default: 'moon' },
          { name: 'media_type', label: 'Tipo (image/video/audio)', type: 'text' },
          { name: 'year_start', label: 'Ano inicial', type: 'text' },
          { name: 'year_end', label: 'Ano final', type: 'text' },
        ],
      },
      {
        id: 'images-asset',
        label: 'Assets de um item',
        path: '/images/asset/{nasa_id}',
        fields: [{ name: 'nasa_id', label: 'NASA ID', type: 'text', required: true }],
      },
    ],
  },
  {
    id: 'osdr',
    name: 'OSDR (Biologia espacial)',
    description: 'Open Science Data Repository — estudos e datasets.',
    endpoints: [
      {
        id: 'osdr-search',
        label: 'Buscar estudos',
        path: '/osdr/search',
        fields: [
          { name: 'term', label: 'Termo', type: 'text', default: 'space' },
          { name: 'size', label: 'Qtd.', type: 'number' },
          { name: 'from', label: 'Offset', type: 'number' },
        ],
      },
      {
        id: 'osdr-meta',
        label: 'Metadados do estudo',
        path: '/osdr/meta/{study_id}',
        fields: [{ name: 'study_id', label: 'ID do estudo', type: 'text', required: true, default: '87' }],
      },
      {
        id: 'osdr-files',
        label: 'Arquivos do estudo',
        path: '/osdr/files/{study_ids}',
        fields: [{ name: 'study_ids', label: 'ID(s) (ex.: 87,137)', type: 'text', required: true, default: '87' }],
      },
    ],
  },
  {
    id: 'ssc',
    name: 'Satellite Situation Center',
    description: 'Localização geocêntrica de naves e estações.',
    endpoints: [
      { id: 'ssc-obs', label: 'Observatórios/naves', path: '/ssc/observatories', fields: [] },
      { id: 'ssc-ground', label: 'Estações terrestres', path: '/ssc/ground-stations', fields: [] },
    ],
  },
  {
    id: 'ssd',
    name: 'SSD/CNEOS (JPL)',
    description: 'Dinâmica do Sistema Solar e estudos de NEOs.',
    endpoints: [
      {
        id: 'ssd-cad',
        label: 'Close Approach',
        path: '/ssd/cad',
        fields: [
          { name: 'date-min', label: 'Data mín.', type: 'date' },
          { name: 'date-max', label: 'Data máx.', type: 'date' },
          { name: 'dist-max', label: 'Dist. máx. (ex.: 0.05)', type: 'text' },
        ],
      },
      {
        id: 'ssd-fireball',
        label: 'Fireballs',
        path: '/ssd/fireball',
        fields: [{ name: 'limit', label: 'Limite', type: 'number' }],
      },
      { id: 'ssd-sentry', label: 'Sentry (risco)', path: '/ssd/sentry', fields: [] },
      { id: 'ssd-scout', label: 'Scout', path: '/ssd/scout', fields: [] },
      { id: 'ssd-nhats', label: 'NHATS', path: '/ssd/nhats', fields: [] },
    ],
  },
  {
    id: 'techport',
    name: 'Techport',
    description: 'Projetos de tecnologia da NASA.',
    endpoints: [
      {
        id: 'techport-list',
        label: 'Listar projetos',
        path: '/techport/projects',
        fields: [{ name: 'updatedSince', label: 'Atualizados desde', type: 'date' }],
      },
      {
        id: 'techport-one',
        label: 'Detalhe do projeto',
        path: '/techport/projects/{project_id}',
        fields: [{ name: 'project_id', label: 'ID do projeto', type: 'number', required: true, default: 157166 }],
      },
    ],
  },
  {
    id: 'techtransfer',
    name: 'TechTransfer',
    description: 'Patentes, software e spinoffs da NASA.',
    endpoints: [
      { id: 'tt-patent', label: 'Patentes', path: '/techtransfer/patent', fields: [{ name: 'query', label: 'Busca (ex.: engine)', type: 'text' }] },
      { id: 'tt-patent-issued', label: 'Patentes emitidas', path: '/techtransfer/patent-issued', fields: [{ name: 'query', label: 'Busca', type: 'text' }] },
      { id: 'tt-software', label: 'Software', path: '/techtransfer/software', fields: [{ name: 'query', label: 'Busca', type: 'text' }] },
      { id: 'tt-spinoff', label: 'Spinoff', path: '/techtransfer/spinoff', fields: [{ name: 'query', label: 'Busca', type: 'text' }] },
    ],
  },
  {
    id: 'tle',
    name: 'TLE (Satélites)',
    description: 'Two-Line Elements de satélites em órbita.',
    endpoints: [
      { id: 'tle-search', label: 'Buscar', path: '/tle', fields: [{ name: 'search', label: 'Nome do satélite', type: 'text' }] },
      {
        id: 'tle-one',
        label: 'Por NORAD ID',
        path: '/tle/{satellite_number}',
        fields: [{ name: 'satellite_number', label: 'NORAD ID', type: 'number', required: true, default: 25544 }],
      },
    ],
  },
  {
    id: 'trek',
    name: 'Trek WMTS (Lua/Marte/Vesta)',
    description: 'Mosaicos globais e índice dos projetos Trek.',
    endpoints: [
      {
        id: 'trek-search',
        label: 'Buscar itens',
        path: '/trek/{body}/search',
        fields: [
          { name: 'body', label: 'Corpo (moon/mars/vesta)', type: 'text', required: true, default: 'mars' },
          { name: 'rows', label: 'Qtd.', type: 'number' },
          { name: 'start', label: 'Offset', type: 'number' },
        ],
      },
      {
        id: 'trek-tile',
        label: 'Tile do mosaico (imagem)',
        path: '/trek/{body}/tile/{tile_matrix}/{tile_row}/{tile_col}',
        binary: true,
        fields: [
          { name: 'body', label: 'Corpo (moon/mars/vesta)', type: 'text', required: true, default: 'moon' },
          { name: 'tile_matrix', label: 'Zoom', type: 'number', required: true, default: 0 },
          { name: 'tile_row', label: 'Linha', type: 'number', required: true, default: 0 },
          { name: 'tile_col', label: 'Coluna', type: 'number', required: true, default: 0 },
        ],
      },
      {
        id: 'trek-caps',
        label: 'Catálogo WMTS (XML)',
        path: '/trek/{body}/capabilities',
        fields: [{ name: 'body', label: 'Corpo (moon/mars/vesta)', type: 'text', required: true, default: 'moon' }],
      },
    ],
  },
]

// Auxiliar para declarar os vários endpoints do DONKI que compartilham os mesmos campos de data.
function donkiDated(slug, label) {
  return {
    id: `donki-${slug}`,
    label,
    path: `/donki/${slug}`,
    fields: [
      { name: 'start_date', label: 'Início', type: 'date' },
      { name: 'end_date', label: 'Fim', type: 'date' },
    ],
  }
}
