const DATABASE_NAME = "lecturas_emax_offline";
const DATABASE_VERSION = 1;

const OUTBOX_STORE = "outbox";
const INMUEBLES_STORE = "inmuebles";
const META_STORE = "meta";


export function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(
            DATABASE_NAME,
            DATABASE_VERSION,
        );

        request.onupgradeneeded = (event) => {
            const database = event.target.result;

            if (!database.objectStoreNames.contains(OUTBOX_STORE)) {
                const outbox = database.createObjectStore(
                    OUTBOX_STORE,
                    {
                        keyPath: "client_uuid",
                    },
                );

                outbox.createIndex(
                    "status",
                    "status",
                    { unique: false },
                );

                outbox.createIndex(
                    "type",
                    "type",
                    { unique: false },
                );

                outbox.createIndex(
                    "created_at",
                    "created_at",
                    { unique: false },
                );
            }

            if (!database.objectStoreNames.contains(INMUEBLES_STORE)) {
                const inmuebles = database.createObjectStore(
                    INMUEBLES_STORE,
                    {
                        keyPath: "codigo_tarjeta",
                    },
                );

                inmuebles.createIndex(
                    "cached_at",
                    "cached_at",
                    { unique: false },
                );
            }

            if (!database.objectStoreNames.contains(META_STORE)) {
                database.createObjectStore(
                    META_STORE,
                    {
                        keyPath: "key",
                    },
                );
            }
        };

        request.onsuccess = () => {
            resolve(request.result);
        };

        request.onerror = () => {
            reject(request.error);
        };

        request.onblocked = () => {
            reject(
                new Error(
                    "IndexedDB está bloqueada por otra pestaña",
                ),
            );
        };
    });
}


export async function putOutboxItem(record) {
    const database = await openDatabase();

    const item = {
        ...record,
        client_uuid: record.client_uuid || crypto.randomUUID(),
        status: record.status || "pending",
        attempts: record.attempts || 0,
        last_error: record.last_error || null,
        created_at: record.created_at || new Date().toISOString(),
    };

    return new Promise((resolve, reject) => {
        const transaction = database.transaction(
            OUTBOX_STORE,
            "readwrite",
        );

        transaction.objectStore(OUTBOX_STORE).put(item);

        transaction.oncomplete = () => {
            database.close();
            resolve(item);
        };

        transaction.onerror = () => {
            database.close();
            reject(transaction.error);
        };

        transaction.onabort = () => {
            database.close();
            reject(transaction.error);
        };
    });
}


export async function getAllOutboxItems() {
    const database = await openDatabase();

    return new Promise((resolve, reject) => {
        const transaction = database.transaction(
            OUTBOX_STORE,
            "readonly",
        );

        const request = transaction
            .objectStore(OUTBOX_STORE)
            .getAll();

        request.onsuccess = () => {
            resolve(request.result);
        };

        request.onerror = () => {
            reject(request.error);
        };

        transaction.oncomplete = () => {
            database.close();
        };
    });
}


export async function deleteOutboxItem(clientUuid) {
    const database = await openDatabase();

    return new Promise((resolve, reject) => {
        const transaction = database.transaction(
            OUTBOX_STORE,
            "readwrite",
        );

        transaction
            .objectStore(OUTBOX_STORE)
            .delete(clientUuid);

        transaction.oncomplete = () => {
            database.close();
            resolve();
        };

        transaction.onerror = () => {
            database.close();
            reject(transaction.error);
        };
    });
}


export async function countPendingItems() {
    const database = await openDatabase();

    return new Promise((resolve, reject) => {
        const transaction = database.transaction(
            OUTBOX_STORE,
            "readonly",
        );

        const request = transaction
            .objectStore(OUTBOX_STORE)
            .index("status")
            .count("pending");

        request.onsuccess = () => {
            resolve(request.result);
        };

        request.onerror = () => {
            reject(request.error);
        };

        transaction.oncomplete = () => {
            database.close();
        };
    });
}


export async function updateOutboxItem(clientUuid, changes) {
    const db = await openDatabase()

    return new Promise((resolve, reject) => {
        const transaction = db.transaction("outbox", "readwrite")
        const store = transaction.objectStore("outbox")
        const request = store.get(clientUuid)

        request.onerror = () => reject(request.error)

        request.onsuccess = () => {
            const currentRecord = request.result

            if (!currentRecord) {
                transaction.abort()
                reject(
                    new Error(
                        `No existe el registro ${clientUuid} en outbox`
                    )
                )
                return
            }

            store.put({
                ...currentRecord,
                ...changes,
                client_uuid: clientUuid,
            })
        }

        transaction.oncomplete = () => resolve(true)
        transaction.onerror = () => reject(transaction.error)
        transaction.onabort = () => {
            reject(
                transaction.error ??
                new Error("La actualización fue cancelada")
            )
        }
    })
}