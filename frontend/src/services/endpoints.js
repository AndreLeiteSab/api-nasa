// Single source of truth describing every gateway endpoint the UI can call.
// Each service groups one or more endpoints; each endpoint declares its path
// template, fields (rendered as a form) and an optional `binary` flag.

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
    id: 'earth',
    name: 'Earth',
    description: 'Imagens de satélite (Landsat 8) por coordenada.',
    endpoints: [
      {
        id: 'earth-imagery',
        label: 'Imagem (PNG)',
        path: '/earth/imagery',
        binary: true,
        fields: [
          { name: 'lat', label: 'Latitude', type: 'number', required: true },
          { name: 'lon', label: 'Longitude', type: 'number', required: true },
          { name: 'dim', label: 'Dimensão (graus)', type: 'number' },
          { name: 'date', label: 'Data', type: 'date' },
        ],
      },
      {
        id: 'earth-assets',
        label: 'Assets (metadados)',
        path: '/earth/assets',
        fields: [
          { name: 'lat', label: 'Latitude', type: 'number', required: true },
          { name: 'lon', label: 'Longitude', type: 'number', required: true },
          { name: 'date', label: 'Data', type: 'date' },
          { name: 'dim', label: 'Dimensão', type: 'number' },
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
    id: 'mars',
    name: 'Mars Rover Photos',
    description: 'Fotos dos rovers em Marte.',
    endpoints: [
      { id: 'mars-rovers', label: 'Listar rovers', path: '/mars-rover/rovers', fields: [] },
      {
        id: 'mars-manifest',
        label: 'Manifesto',
        path: '/mars-rover/manifests/{rover}',
        fields: [{ name: 'rover', label: 'Rover', type: 'text', required: true, default: 'curiosity' }],
      },
      {
        id: 'mars-photos',
        label: 'Fotos',
        path: '/mars-rover/rovers/{rover}/photos',
        fields: [
          { name: 'rover', label: 'Rover', type: 'text', required: true, default: 'curiosity' },
          { name: 'sol', label: 'Sol (dia marciano)', type: 'number' },
          { name: 'earth_date', label: 'Data terrestre', type: 'date' },
          { name: 'camera', label: 'Câmera (ex.: NAVCAM)', type: 'text' },
          { name: 'page', label: 'Página', type: 'number' },
        ],
      },
      {
        id: 'mars-latest',
        label: 'Fotos recentes',
        path: '/mars-rover/rovers/{rover}/latest_photos',
        fields: [{ name: 'rover', label: 'Rover', type: 'text', required: true, default: 'curiosity' }],
      },
    ],
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
    id: 'insight',
    name: 'InSight (Marte)',
    description: 'Clima em Marte (missão InSight — dados podem estar vazios).',
    endpoints: [{ id: 'insight-weather', label: 'Clima', path: '/insight', fields: [] }],
  },
  {
    id: 'exoplanet',
    name: 'Exoplanet Archive',
    description: 'Consulta ao arquivo de exoplanetas.',
    endpoints: [
      {
        id: 'exo-query',
        label: 'Consultar',
        path: '/exoplanet',
        fields: [
          { name: 'table', label: 'Tabela', type: 'text', default: 'exoplanets' },
          { name: 'select', label: 'Colunas (select)', type: 'text' },
          { name: 'where', label: 'Filtro (where)', type: 'text' },
        ],
      },
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
]

// Helper to declare the many DONKI endpoints that share the same date fields.
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
