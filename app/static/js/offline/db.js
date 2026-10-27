const DATABASE_NAME = "lecturas_emax_offline";
const DATABASE_VERSION = 2;

const OUTBOX_STORE = "outbox";
const INMUEBLES_STORE = "inmuebles";
const META_STORE = "meta";

const CONTADOR_INDEX = "contador_busqueda";
const RUTA_INDEX = "ruta_busqueda";
const COLLECTION_INDEX = "offline_collection_key";

const SIN_RUTA_INDEX_VALUE = "__SIN_RUTA__";


function normalizeCode(value) {
    return String(value ?? "").trim();
}

function normalizeCounter(value) {
    const normalized = String(value ?? "")
        .trim()
        .toUpperCase();

    if (
        !normalized
        || normalized === "0"
        || normalized === "NULL"
        || normalized === "NONE"
    ) {
        return undefined;
    }

    return normalized;
}

function normalizeRoute(value) {
    return String(value ?? "").trim();
}


function getRouteIndexValue(value) {
    return normalizeRoute(value)
        || SIN_RUTA_INDEX_VALUE;
}


function getRouteCollectionKey({
    ruta = null,
    sin_ruta = false,
}) {
    const normalizedRoute = normalizeRoute(ruta);

    if (sin_ruta && normalizedRoute) {
        throw new Error(
            "No se puede indicar ruta y sin_ruta al mismo tiempo"
        );
    }

    if (sin_ruta) {
        return "route-download:sin-ruta";
    }

    if (!normalizedRoute) {
        throw new Error(
            "La ruta es obligatoria"
        );
    }

    return `route-download:ruta:${normalizedRoute}`;
}

export function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open(
            DATABASE_NAME,
            DATABASE_VERSION,
        );

        request.onupgradeneeded = (event) => {
            const database = event.target.result;
            const upgradeTransaction =
                event.target.transaction;

            let outbox;

            if (
                !database.objectStoreNames.contains(
                    OUTBOX_STORE
                )
            ) {
                outbox = database.createObjectStore(
                    OUTBOX_STORE,
                    {
                        keyPath: "client_uuid",
                    },
                );
            } else {
                outbox = upgradeTransaction.objectStore(
                    OUTBOX_STORE
                );
            }

            if (!outbox.indexNames.contains("status")) {
                outbox.createIndex(
                    "status",
                    "status",
                    { unique: false },
                );
            }

            if (!outbox.indexNames.contains("type")) {
                outbox.createIndex(
                    "type",
                    "type",
                    { unique: false },
                );
            }

            if (
                !outbox.indexNames.contains(
                    "created_at"
                )
            ) {
                outbox.createIndex(
                    "created_at",
                    "created_at",
                    { unique: false },
                );
            }

            let inmuebles;

            if (
                !database.objectStoreNames.contains(
                    INMUEBLES_STORE
                )
            ) {
                inmuebles = database.createObjectStore(
                    INMUEBLES_STORE,
                    {
                        keyPath: "codigo_tarjeta",
                    },
                );
            } else {
                inmuebles = upgradeTransaction.objectStore(
                    INMUEBLES_STORE
                );
            }

            if (
                !inmuebles.indexNames.contains(
                    "cached_at"
                )
            ) {
                inmuebles.createIndex(
                    "cached_at",
                    "cached_at",
                    { unique: false },
                );
            }

            if (
                !inmuebles.indexNames.contains(
                    CONTADOR_INDEX
                )
            ) {
                inmuebles.createIndex(
                    CONTADOR_INDEX,
                    "contador_busqueda",
                    { unique: false },
                );
            }

            if (
                !inmuebles.indexNames.contains(
                    RUTA_INDEX
                )
            ) {
                inmuebles.createIndex(
                    RUTA_INDEX,
                    "ruta_busqueda",
                    { unique: false },
                );
            }

            if (
                !inmuebles.indexNames.contains(
                    COLLECTION_INDEX
                )
            ) {
                inmuebles.createIndex(
                    COLLECTION_INDEX,
                    "offline_collection_key",
                    { unique: false },
                );
            }

            if (
                !database.objectStoreNames.contains(
                    META_STORE
                )
            ) {
                database.createObjectStore(
                    META_STORE,
                    {
                        keyPath: "key",
                    },
                );
            }

            /*
            * Completa los campos de búsqueda de los
            * inmuebles almacenados con la versión 1.
            */
            if (event.oldVersion < 2) {
                const cursorRequest =
                    inmuebles.openCursor();

                cursorRequest.onsuccess = (
                    cursorEvent
                ) => {
                    const cursor =
                        cursorEvent.target.result;

                    if (!cursor) {
                        return;
                    }

                    const record = cursor.value;
                    const code = normalizeCode(
                        record.codigo_tarjeta
                    );

                    cursor.update({
                        ...record,
                        contador_busqueda:
                            normalizeCounter(record.nit),
                        ruta_busqueda:
                            getRouteIndexValue(
                                record.ruta
                            ),
                        offline_collection_key:
                            record.offline_collection_key
                            || `individual:${code}`,
                    });

                    cursor.continue();
                };
            }
        };

        request.onsuccess = () => {
            const database = request.result;

            database.onversionchange = () => {
                database.close();
            };

            resolve(database);
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

export async function putInmueble(inmueble) {
    if (!inmueble?.codigo_tarjeta) {
        throw new Error(
            "El inmueble no contiene codigo_tarjeta"
        )
    }

    const normalizedCode = normalizeCode(
    inmueble.codigo_tarjeta
    );

    const record = {
        ...inmueble,

        codigo_tarjeta:
            normalizedCode,

        contador_busqueda:
            normalizeCounter(inmueble.nit),

        ruta_busqueda:
            getRouteIndexValue(inmueble.ruta),

        offline_collection_key:
            inmueble.offline_collection_key
            || `individual:${normalizedCode}`,

        cached_at:
            new Date().toISOString(),
    };
}

export async function getInmuebleByCodigo(codigo) {
    const normalizedCode = String(codigo ?? "").trim()

    if (!normalizedCode) {
        return null
    }

    const db = await openDatabase()

    return new Promise((resolve, reject) => {
        const transaction = db.transaction(
            "inmuebles",
            "readonly"
        )

        const store =
            transaction.objectStore("inmuebles")

        const request = store.get(normalizedCode)

        request.onsuccess = () => {
            resolve(request.result ?? null)
        }

        request.onerror = () => {
            reject(request.error)
        }
    })
}

export async function getInmuebleByContador(
    contador
) {
    const normalizedCounter =
        normalizeCounter(contador);

    if (!normalizedCounter) {
        return null;
    }

    const database = await openDatabase();

    return new Promise((resolve, reject) => {
        const transaction =
            database.transaction(
                INMUEBLES_STORE,
                "readonly",
            );

        const request = transaction
            .objectStore(INMUEBLES_STORE)
            .index(CONTADOR_INDEX)
            .get(normalizedCounter);

        request.onsuccess = () => {
            resolve(request.result ?? null);
        };

        request.onerror = () => {
            reject(request.error);
        };

        transaction.oncomplete = () => {
            database.close();
        };
    });
}

export async function replaceRouteDownload(
    download
) {
    const inmuebles = download?.inmuebles;

    if (!Array.isArray(inmuebles)) {
        throw new Error(
            "La descarga no contiene una lista de inmuebles"
        );
    }

    const periodoProceso = String(
        download.periodo_proceso ?? ""
    ).trim();

    if (
        !/^\d{4}-(0[1-9]|1[0-2])$/.test(
            periodoProceso
        )
    ) {
        throw new Error(
            "periodo_proceso debe usar el formato YYYY-MM"
        );
    }

    const collectionKey =
        getRouteCollectionKey({
            ruta: download.ruta,
            sin_ruta:
                download.sin_ruta === true,
        });

    const downloadedAt =
        download.descargado_en
        || new Date().toISOString();

    if (
        Number(download.total)
        !== inmuebles.length
    ) {
        throw new Error(
            "La cantidad recibida no coincide con total"
        );
    }

    const records = inmuebles.map(
        inmueble => {
            const code = normalizeCode(
                inmueble.codigo_tarjeta
            );

            if (!code) {
                throw new Error(
                    "Un inmueble no contiene codigo_tarjeta"
                );
            }

            return {
                ...inmueble,
                codigo_tarjeta: code,

                contador_busqueda:
                    normalizeCounter(
                        inmueble.nit
                    ),

                ruta_busqueda:
                    getRouteIndexValue(
                        inmueble.ruta
                    ),

                offline_collection_key:
                    collectionKey,

                offline_periodo_proceso:
                    periodoProceso,

                cached_at: downloadedAt,
            };
        }
    );

    const metadata = {
        key: collectionKey,
        type: "route_download",

        collection_key: collectionKey,

        ruta: download.sin_ruta
            ? null
            : normalizeRoute(download.ruta),

        sin_ruta:
            download.sin_ruta === true,

        periodo_proceso:
            periodoProceso,

        cantidad:
            records.length,

        descargado_en:
            downloadedAt,

        almacenado_en:
            new Date().toISOString(),
    };

    const database = await openDatabase();

    return new Promise((resolve, reject) => {
        const transaction =
            database.transaction(
                [
                    INMUEBLES_STORE,
                    META_STORE,
                ],
                "readwrite",
            );

        const inmuebleStore =
            transaction.objectStore(
                INMUEBLES_STORE
            );

        const metadataStore =
            transaction.objectStore(
                META_STORE
            );

        const collectionIndex =
            inmuebleStore.index(
                COLLECTION_INDEX
            );

        let operationError = null;

        const abortTransaction = error => {
            operationError = error;

            try {
                transaction.abort();
            } catch {
                // La transacción ya fue cancelada.
            }
        };

        /*
         * Primero elimina únicamente los registros
         * de la descarga anterior de esta ruta.
         *
         * Todos los DELETE, PUT y metadata pertenecen
         * a la misma transacción.
         */
        const cursorRequest =
            collectionIndex.openCursor(
                IDBKeyRange.only(
                    collectionKey
                )
            );

        cursorRequest.onerror = () => {
            abortTransaction(
                cursorRequest.error
                || new Error(
                    "No se pudo limpiar la descarga anterior"
                )
            );
        };

        cursorRequest.onsuccess = event => {
            const cursor =
                event.target.result;

            if (cursor) {
                cursor.delete();
                cursor.continue();
                return;
            }

            try {
                for (const record of records) {
                    inmuebleStore.put(record);
                }

                metadataStore.put(metadata);
            } catch (error) {
                abortTransaction(error);
            }
        };

        transaction.oncomplete = () => {
            database.close();

            resolve({
                ...metadata,
                ok: true,
            });
        };

        transaction.onerror = () => {
            operationError =
                operationError
                || transaction.error;
        };

        transaction.onabort = () => {
            database.close();

            reject(
                operationError
                || transaction.error
                || new Error(
                    "La descarga no pudo almacenarse"
                )
            );
        };
    });
}

export async function getRouteDownloadMetadata({
    ruta = null,
    sin_ruta = false,
}) {
    const collectionKey =
        getRouteCollectionKey({
            ruta,
            sin_ruta,
        });

    const database = await openDatabase();

    return new Promise((resolve, reject) => {
        const transaction =
            database.transaction(
                META_STORE,
                "readonly",
            );

        const request = transaction
            .objectStore(META_STORE)
            .get(collectionKey);

        request.onsuccess = () => {
            resolve(request.result ?? null);
        };

        request.onerror = () => {
            reject(request.error);
        };

        transaction.oncomplete = () => {
            database.close();
        };
    });
}


export async function countRouteInmuebles({
    ruta = null,
    sin_ruta = false,
}) {
    const collectionKey =
        getRouteCollectionKey({
            ruta,
            sin_ruta,
        });

    const database = await openDatabase();

    return new Promise((resolve, reject) => {
        const transaction =
            database.transaction(
                INMUEBLES_STORE,
                "readonly",
            );

        const request = transaction
            .objectStore(INMUEBLES_STORE)
            .index(COLLECTION_INDEX)
            .count(collectionKey);

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