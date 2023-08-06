dummy_index = {
    'index_prefix': 'posts',
    'index_settings': {
        'index.refresh_interval': '2s'
    },
    'index_mappings': {
        'id': {
            'type': 'keyword'
        },
        'author': {
            'type': 'keyword'
        },
        'title': {
            'type': 'keyword'
        },
        'description': {
            'type': 'text'
        },
        'content': {
            'type': 'text'
        },
        'timestamp': {
            'type': 'date',
            'format': 'yyyy-MM-dd HH:mm:ss||epoch_millis'

        }
    }
}
