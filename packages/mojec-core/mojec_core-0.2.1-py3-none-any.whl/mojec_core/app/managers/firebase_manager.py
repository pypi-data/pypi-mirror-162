from firebase_admin import firestore

from mojec_core.utils import log_exception


class FirebaseManager:
    db = firestore.client()

    def assign_workorder(self, wo):
        try:
            doc_ref = self.db.collection('WORKORDERS').document(
                wo.uid.__str__())
            data = doc_ref.get().to_dict()
            print("data", data)
            data['status'] = 'assigned'
            doc_ref.set(data)
        except Exception as ex:
            log_exception("FirebaseManager.assign_workorder", ex)

    def remove_workorder(self, uid):
        try:
            doc_ref = self.db.collection('WORKORDERS').document(str(uid))
            doc_ref.delete()
        except Exception as ex:
            log_exception("FirebaseManager.remove_workorder", ex)
