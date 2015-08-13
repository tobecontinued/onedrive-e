import io
import unittest
from ciso8601 import parse_datetime

import requests_mock

from requests import codes

from onedrive_d.api import drives
from onedrive_d.api import facets
from onedrive_d.api import items
from onedrive_d.api import options
from onedrive_d.api import resources
from onedrive_d.tests import get_data
from onedrive_d.tests.api import drive_factory


class TestDriveRoot(unittest.TestCase):
    def setUp(self):
        self.root = drive_factory.get_sample_drive_root()
        self.account = self.root.account

    def test_get_all_drives(self):
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                response_drives = [get_data('drive.json'), get_data('drive.json')]
                ids = [str(i) for i in range(0, 2)]
                for d in response_drives:
                    d['id'] = ids.pop(0)
                context.status_code = codes.ok
                return {'value': response_drives}

            mock.get(self.account.client.API_URI + '/drives', json=callback)
            all_drives = self.root.get_all_drives()
            all_ids = [str(i) for i in range(0, 2)]
            for i, x in all_drives.items():
                self.assertIn(i, all_ids)
                self.assertIsInstance(x, drives.DriveObject)
                all_ids.remove(i)
            self.assertEqual(0, len(all_ids))

    def run_get_drive(self, drive_id):
        """
        :param str | None drive_id:
        """
        with requests_mock.Mocker() as mock:
            path = '/drive'
            if drive_id is not None:
                path += 's/' + drive_id
            mock.get(self.account.client.API_URI + path, json=get_data('drive.json'))
            if drive_id is not None:
                drive = self.root.get_drive(drive_id)
            else:
                drive = self.root.get_default_drive()
            self.assertIsInstance(drive, drives.DriveObject)

    def test_get_drive(self):
        self.run_get_drive('123')

    def test_get_default_drive(self):
        self.run_get_drive(None)


class TestDriveObject(unittest.TestCase):
    def setUp(self):
        self.data = get_data('drive.json')
        self.drive = drive_factory.get_sample_drive_object(self.data)

    def test_parse(self):
        self.assertEqual(self.data['id'], self.drive.id)
        self.assertEqual(self.data['driveType'], self.drive.type)
        self.assertIsInstance(self.drive.quota, facets.QuotaFacet)

    def test_get_root(self):
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                data = get_data('drive_root.json')
                context.status_code = codes.ok
                return data

            mock.get(self.drive.drive_uri + '/root?expand=children', json=callback)
            root_item = self.drive.get_root_dir(list_children=True)
            self.assertIsInstance(root_item, items.OneDriveItem)

    def use_item_collection(self, method_name, url, params):
        item_set = get_data('item_collection.json')['value']
        item_names = [i['name'] for i in item_set]
        next_link = 'https://get_children'
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                data = {
                    'value': [item_set.pop(0)]
                }
                if len(item_set) > 0:
                    data['@odata.nextLink'] = next_link
                context.status_code = codes.ok
                return data

            mock.get(url, json=callback)
            mock.get(next_link, json=callback)
            collection = getattr(self.drive, method_name)(**params)
            received_names = []
            while collection.has_next:
                page = collection.get_next()
                for i in page:
                    received_names.append(i.name)
            self.assertListEqual(item_names, received_names)

    def test_get_children(self):
        self.use_item_collection(
            'get_children',
            self.drive.get_item_uri(None, 'foo/bar') + ':/children',
            {'item_path': 'foo/bar'})

    def test_search(self):
        self.use_item_collection(
            'search',
            self.drive.get_item_uri(None, 'foo/bar') + '/view.search?q=try&select=name,size',
            {'item_path': 'foo/bar', 'keyword': 'try', 'select': ['name', 'size']})

    def test_create_dir(self):
        """
        https://github.com/OneDrive/onedrive-api-docs/blob/master/items/create.md
        """
        folder_name = 'Documents'
        conflict_behavior = options.NameConflictBehavior.REPLACE
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                data = request.json()
                self.assertEqual(folder_name, data['name'])
                self.assertDictEqual({}, data['folder'])
                self.assertEqual(conflict_behavior, data['@name.conflictBehavior'])
                context.status_code = codes.created
                return {
                    'id': '000aaa!100',
                    'name': folder_name,
                    'folder': {
                        'childCount': 0
                    }
                }

            mock.post(self.drive.get_item_uri(None, None), json=callback, status_code=codes.created)
            item = self.drive.create_dir(name=folder_name, conflict_behavior=conflict_behavior)
            self.assertIsInstance(item, items.OneDriveItem)

    def test_delete_item(self):
        with requests_mock.Mocker() as mock:
            mock.delete(self.drive.get_item_uri(None, None), status_code=codes.no_content)
            self.drive.delete_item()

    def test_update_root(self):
        self.assertRaises(ValueError, self.drive.update_item, None, None)

    def test_update_item(self):
        new_params = {
            'item_id': '123',
            'new_name': 'whatever.doc',
            'new_description': 'This is a dummy description.',
            'new_parent_reference': resources.ItemReference.build(drive_id='aaa', id='012'),
            'new_file_system_info': facets.FileSystemInfoFacet(
                created_time=parse_datetime('1971-01-01T02:03:04Z'),
                modified_time=parse_datetime('2008-01-02T03:04:05.06Z'))
        }
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                json = request.json()
                self.assertEqual(json['name'], new_params['new_name'])
                self.assertEqual(json['description'], new_params['new_description'])
                self.assertDictEqual(json['parentReference'], new_params['new_parent_reference'].data)
                self.assertDictEqual(json['fileSystemInfo'], new_params['new_file_system_info'].data)
                return get_data('image_item.json')

            mock.patch(self.drive.get_item_uri(new_params['item_id'], None), json=callback)
            self.drive.update_item(**new_params)

    def test_update_item_errors(self):
        self.assertRaises(ValueError, self.drive.update_item, None, None)  # Error when no specific item is target.
        self.assertRaises(ValueError, self.drive.update_item, None, 'foo')  # Error when nothing is set.

    def test_get_file_content(self):
        with requests_mock.Mocker() as mock:
            mock.get(self.drive.get_item_uri(item_id='123', item_path=None) + '/content', content=b'hel',
                     status_code=codes.ok)
            data = self.drive.get_file_content(item_id='123')
            self.assertEqual(b'hel', data)

    def test_download_small_file(self):
        self.drive.MAX_GET_SIZE = 10
        data = b'12345'
        output = io.BytesIO()
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                self.assertNotIn('Range', request.headers)
                context.status_code = codes.ok
                return data

            mock.get(self.drive.get_item_uri(item_id='123', item_path=None) + '/content', content=callback)
            self.drive.download_file(file=output, size=len(data), item_id='123')
            self.assertEqual(data, output.getvalue())

    def test_download_large_file(self):
        self.drive.MAX_GET_SIZE = 2
        in_data = b'12345'
        output = io.BytesIO()
        expected_ranges = ['0-1', '2-3', '4-4']
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                self.assertIn('Range', request.headers)
                r = expected_ranges.pop(0)
                self.assertEqual('bytes=' + r, request.headers['Range'])
                f, t = request.headers['Range'].split('=', 1)[1].split('-')
                context.status_code = codes.partial
                return in_data[int(f): int(t) + 1]

            mock.get(self.drive.get_item_uri(item_id='123', item_path=None) + '/content', content=callback)
            self.drive.download_file(file=output, size=len(in_data), item_id='123', chunk_size=2)
        self.assertEqual(in_data, output.getvalue())

    def test_upload_small_file(self):
        self.drive.MAX_PUT_SIZE = 10
        in_fd = io.BytesIO(b'12345')
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                name = request.path_url.split('/')[-2][:-1]
                self.assertEqual('test', name)
                self.assertEqual(5, len(request.body.getvalue()))
                qs = request.path_url.split('?', 1)[1]
                self.assertEqual('@name.conflictBehavior=' + options.NameConflictBehavior.FAIL, qs)
                data = {
                    'id': 'abc',
                    'name': name,
                    'size': 5,
                    'file': {},
                }
                context.status_code = codes.created
                return data

            mock.put(self.drive.get_item_uri('123', None) + ':/test:/content', json=callback)
            item = self.drive.upload_file('test', data=in_fd, size=5, parent_id='123',
                                          conflict_behavior=options.NameConflictBehavior.FAIL)
            self.assertIsInstance(item, items.OneDriveItem)

    def test_upload_large_file(self):
        self.drive.MAX_PUT_SIZE = 2
        session_url = 'https://foo/bar/accept_data'
        input = io.BytesIO(b'12345')
        output = io.BytesIO()
        expected_ranges = ['0-1/5', '2-3/5', '4-4/5']
        with requests_mock.Mocker() as mock:
            def create_session(request, context):
                body = request.json()['item']
                self.assertEqual('test', body['name'])
                self.assertEqual(options.NameConflictBehavior.RENAME, body['@name.conflictBehavior'])
                context.status_code = codes.ok
                return {
                    'uploadUrl': session_url,
                    'expirationDateTime': '2020-01-01T00:00:00.0Z',
                    'nextExpectedRanges': ['0-']
                }

            def accept_data(request, context):
                self.assertEqual(expected_ranges.pop(0), request.headers['Content-Range'])
                self.assertLessEqual(len(request.body), self.drive.MAX_PUT_SIZE)
                output.write(request.body)
                context.status_code = codes.accepted
                return {
                    'uploadUrl': session_url,
                    'expirationDateTime': '2020-01-01T00:00:00.0Z',
                }

            mock.post(self.drive.get_item_uri(item_id='123', item_path=None) + ':/test:/upload.createSession',
                      json=create_session)
            mock.put(session_url, json=accept_data)
            self.drive.upload_file('test', data=input, size=5, parent_id='123',
                                   conflict_behavior=options.NameConflictBehavior.RENAME)
            self.assertEqual(input.getvalue(), output.getvalue())

    def test_copy_item(self):
        new_parent = resources.ItemReference.build(id='123abc', path='/foo/bar')
        new_name = '456.doc'
        with requests_mock.Mocker() as mock:
            def callback(request, context):
                # Verify that necessary headers are properly set.
                headers = request.headers
                self.assertIn('Content-Type', headers)
                self.assertEqual('application/json', headers['Content-Type'])
                self.assertIn('Prefer', headers)
                self.assertEqual('respond-async', headers['Prefer'])
                # Verify that request body is correct.
                body = request.json()
                self.assertEqual(new_name, body['name'])
                self.assertDictEqual(new_parent.data, body['parentReference'])
                # Set response.
                context.status_code = codes.ok
                context.headers['Location'] = 'https://foo.bar/monitor'
                return None

            mock.post(self.drive.get_item_uri(None, '123') + ':/action.copy', content=callback)
            session = self.drive.copy_item(new_parent, item_path='123', new_name=new_name)
            self.assertIsInstance(session, resources.AsyncCopySession)

    def test_copy_item_errors(self):
        self.assertRaises(ValueError, self.drive.copy_item, {}, item_path='foo')
        self.assertRaises(ValueError, self.drive.copy_item,
                          resources.ItemReference.build(id='123abc', path='/foo/bar'),
                          None, None)

if __name__ == '__main__':
    unittest.main()
